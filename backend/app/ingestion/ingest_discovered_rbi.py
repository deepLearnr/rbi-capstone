"""Safely ingest verified PDF or HTML circular content from official RBI pages.

Discovery is read-only. This module defaults to dry-run; database writes require
--write. HTML-only pages are ingested only when their metadata and substantial
source content can be independently re-verified.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
import tempfile
from datetime import date
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from app.ingestion.discover_rbi import (
    ALLOWED_HOSTS,
    Candidate,
    USER_AGENT,
    discover,
    official_rbi_url,
    fetch_html,
    parse_detail,
)

MAX_PDF_BYTES = 30 * 1024 * 1024
PDF_TIMEOUT_SECONDS = 25
EMBED_BATCH_SIZE = 16
EMBEDDING_MODEL = "intfloat/multilingual-e5-small"
PLACEHOLDER_TITLES = {
    "", "untitled rbi circular candidate", "index to rbi circulars",
    "reserve bank of india", "official website of reserve bank of india",
    "unknown", "untitled",
    "function detectmob() {",
}


def validate_candidate(candidate: Candidate, *, allow_html: bool = False) -> tuple[bool, str]:
    """Return whether candidate metadata is safe enough to consider for ingestion."""
    if not official_rbi_url(candidate.source_url):
        return False, "source URL is not HTTPS on an approved RBI host"
    if candidate.pdf_url:
        if not official_rbi_url(candidate.pdf_url):
            return False, "PDF URL is not HTTPS on an approved RBI host"
        parsed_pdf = urlparse(candidate.pdf_url)
        parsed_source = urlparse(candidate.source_url)
        if (parsed_pdf.hostname or "").lower() not in ALLOWED_HOSTS:
            return False, "PDF host is not approved"
        if not parsed_pdf.path.lower().endswith(".pdf"):
            return False, "link does not point directly to a .pdf resource"
        if (
            parsed_pdf.hostname.lower() == (parsed_source.hostname or "").lower()
            and parsed_pdf.path.rstrip("/").lower() == parsed_source.path.rstrip("/").lower()
            and parsed_pdf.query == parsed_source.query
        ):
            return False, "PDF link points back to the circular HTML page"
    elif not allow_html:
        return False, "no eligible PDF link; HTML-only ingestion is not enabled"
    title = " ".join((candidate.title or "").split())
    title_lower = title.lower()
    if (
        title_lower in PLACEHOLDER_TITLES
        or len(title) < 8
        or title_lower.startswith(("function ", "//redirect", "javascript:", "var "))
        or "detectmob" in title_lower
        or "redirect to mobile site" in title_lower
    ):
        return False, "title is missing, a placeholder, or page-script text"
    if not candidate.reference or not re.fullmatch(
        r"[A-Za-z][A-Za-z0-9()./-]{1,40}/\d{4}[-–]\d{2,4}/[A-Za-z0-9-]{1,30}",
        candidate.reference.strip(),
    ):
        return False, "RBI reference is missing or has an unexpected format"
    try:
        date.fromisoformat(candidate.publication_date or "")
    except (TypeError, ValueError):
        return False, "publication date is missing or not a valid ISO date"
    return True, "eligible"


def safe_filename(candidate: Candidate) -> str:
    ref = (candidate.reference or "RBI-circular").replace("–", "-")
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", ref).strip("._-")
    return (stem or "RBI-circular") + ".pdf"


def safe_html_filename(candidate: Candidate) -> str:
    return safe_filename(candidate)[:-4] + ".html"


def _prepare_html_chunks(candidate: Candidate):
    """Fetch the source page again and verify metadata/content before writes."""
    from app.ingestion.rbi_html_content import extract_circular_html_content, chunk_html_content

    html, final_url = fetch_html(candidate.source_url)
    live = parse_detail(html, final_url)
    if live.reference != candidate.reference:
        raise ValueError("RBI reference changed between discovery and ingestion")
    if live.publication_date != candidate.publication_date:
        raise ValueError("Publication date changed between discovery and ingestion")
    if " ".join(live.title.split()).casefold() != " ".join(candidate.title.split()).casefold():
        raise ValueError("Circular title changed between discovery and ingestion")
    content = extract_circular_html_content(html, candidate)
    chunks = chunk_html_content(content)
    if not chunks:
        raise ValueError("HTML extraction produced no usable chunks")
    return content, chunks


def download_pdf(url: str, destination: Path) -> int:
    """Download an official PDF with redirect, size, timeout and signature checks."""
    if not official_rbi_url(url):
        raise ValueError("Refusing non-official or non-HTTPS PDF URL")
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/pdf"})
    try:
        with urlopen(request, timeout=PDF_TIMEOUT_SECONDS) as response:
            final_url = response.geturl()
            if not official_rbi_url(final_url):
                raise ValueError(f"PDF redirected outside the RBI host allowlist: {final_url}")
            length = response.headers.get("Content-Length")
            if length:
                try:
                    if int(length) > MAX_PDF_BYTES:
                        raise ValueError("PDF exceeds maximum permitted size")
                except ValueError as exc:
                    if str(exc) == "PDF exceeds maximum permitted size":
                        raise
            payload = response.read(MAX_PDF_BYTES + 1)
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError(f"PDF download failed: {exc}") from exc
    if len(payload) > MAX_PDF_BYTES:
        raise ValueError("PDF exceeds maximum permitted size")
    if not payload.startswith(b"%PDF-"):
        raise ValueError("Downloaded content does not have a valid PDF signature")
    destination.write_bytes(payload)
    return len(payload)


def _find_duplicate(session, candidate: Candidate, source_file: str):
    from sqlalchemy import or_, select
    from app.models.document import Document

    conditions = [Document.source_url == candidate.source_url]
    if candidate.reference:
        conditions.append(Document.rbi_reference == candidate.reference)
    conditions.append(Document.source_file == source_file)
    return session.scalar(select(Document).where(or_(*conditions)).limit(1))


def _embed_new_chunks(chunks) -> list[list[float]]:
    """Compute embeddings for this candidate only; fail before database writes."""
    from app.embeddings.service import embed_passages

    vectors: list[list[float]] = []
    for start in range(0, len(chunks), EMBED_BATCH_SIZE):
        texts = [chunk.content for chunk in chunks[start:start + EMBED_BATCH_SIZE]]
        if texts:
            batch = embed_passages(texts)
            if len(batch) != len(texts):
                raise RuntimeError("Embedding service returned an unexpected vector count")
            for vector in batch:
                if len(vector) != 384:
                    raise RuntimeError("Embedding service returned a vector with unexpected dimensions")
            vectors.extend(batch)
    return vectors


def ingest_candidate(candidate: Candidate, *, write: bool = False) -> dict:
    """Inspect a candidate and optionally ingest its PDF or verified HTML content."""
    is_html = not bool(candidate.pdf_url)
    eligible, reason = validate_candidate(candidate, allow_html=is_html)
    result = {
        "title": candidate.title,
        "reference": candidate.reference,
        "source_url": candidate.source_url,
        "status": "skipped",
        "reason": reason,
    }
    if not eligible:
        return result

    source_file = safe_html_filename(candidate) if is_html else safe_filename(candidate)
    prepared_html = None
    if is_html:
        try:
            prepared_html = _prepare_html_chunks(candidate)
        except Exception as exc:
            result.update(
                status="skipped",
                reason=f"official HTML content could not be verified: {exc}",
            )
            return result

    if not write:
        if is_html:
            content, chunks = prepared_html
            result.update(
                status="dry_run",
                reason=(
                    f"eligible official HTML content ({len(content)} chars, "
                    f"{len(chunks)} chunks); no database changes made"
                ),
            )
        else:
            result.update(status="dry_run", reason="eligible PDF; no database changes made")
        return result

    from app.db.session import SessionLocal
    from app.models.document import Document
    from app.models.document_chunk import DocumentChunk

    with SessionLocal() as session:
        existing = _find_duplicate(session, candidate, source_file)
        if existing is not None:
            result.update(
                status="duplicate",
                reason=f"matching document already exists (id={existing.id})",
                document_id=existing.id,
            )
            return result

    if is_html:
        content, chunks = prepared_html
        source_size = len(content.encode("utf-8"))
        ingestion_method = "official_rbi_discovery_html"
    else:
        from app.ingestion.pdf_extractor import extract_pdf_pages
        from app.ingestion.regulatory_chunker import chunk_regulatory_pages

        with tempfile.TemporaryDirectory(prefix="rbi-saathi-") as temp_dir:
            pdf_path = Path(temp_dir) / source_file
            source_size = download_pdf(candidate.pdf_url, pdf_path)
            pages = extract_pdf_pages(pdf_path)
            chunks = chunk_regulatory_pages(pages)
        if not chunks:
            raise RuntimeError("PDF extraction produced no usable chunks")
        ingestion_method = "official_rbi_discovery_pdf"

    vectors = _embed_new_chunks(chunks)

    with SessionLocal() as session:
        try:
            existing = _find_duplicate(session, candidate, source_file)
            if existing is not None:
                session.rollback()
                result.update(
                    status="duplicate",
                    reason=f"matching document already exists (id={existing.id})",
                    document_id=existing.id,
                )
                return result

            document = Document(
                title=" ".join(candidate.title.split()),
                document_type="regulatory_circular",
                rbi_reference=candidate.reference,
                publication_date=date.fromisoformat(candidate.publication_date),
                department=candidate.department,
                source_url=candidate.source_url,
                source_file=source_file,
                language="en",
                description=(
                    "Discovered from an official RBI circular page; source metadata "
                    "captured from that page. Content extracted from HTML."
                    if is_html else
                    "Discovered from an official RBI circular page; source metadata "
                    "captured from that page. Content extracted from PDF."
                ),
            )
            session.add(document)
            session.flush()

            for chunk, vector in zip(chunks, vectors):
                metadata = dict(chunk.metadata or {})
                metadata.update({
                    "source_url": candidate.source_url,
                    "rbi_reference": candidate.reference,
                    "ingestion_method": ingestion_method,
                })
                session.add(DocumentChunk(
                    document_id=document.id,
                    chunk_index=chunk.chunk_index,
                    content=chunk.content,
                    page_start=chunk.page_start,
                    page_end=chunk.page_end,
                    section_reference=chunk.section_reference,
                    heading=chunk.heading,
                    heading_path=chunk.heading_path,
                    chunk_metadata=metadata,
                    content_hash=hashlib.sha256(chunk.content.encode("utf-8")).hexdigest(),
                    embedding=vector,
                    embedding_model=EMBEDDING_MODEL,
                ))
            session.commit()
            result.update(
                status="ingested",
                reason=(
                    f"saved verified {'HTML content' if is_html else 'PDF'} "
                    f"({source_size} bytes), {len(chunks)} chunks embedded"
                ),
                document_id=document.id,
                chunks=len(chunks),
            )
            return result
        except Exception:
            session.rollback()
            raise



def main() -> int:
    parser = argparse.ArgumentParser(
        description="Discover RBI circulars and safely ingest eligible official PDF/HTML content (dry-run by default)."
    )
    parser.add_argument("--index-url", help="Official RBI index URL or direct detail page URL.")
    parser.add_argument("--max-candidates", type=int, default=25)
    parser.add_argument("--delay", type=float, default=0.25)
    parser.add_argument("--write", action="store_true", help="Actually insert eligible documents and their embedded chunks.")
    args = parser.parse_args()

    from app.ingestion.discover_rbi import DEFAULT_INDEX_URL
    index_url = args.index_url or DEFAULT_INDEX_URL
    try:
        candidates = discover(index_url, args.max_candidates, args.delay)
    except (RuntimeError, ValueError) as exc:
        print(f"DISCOVERY FAILED: {exc}", file=sys.stderr)
        return 2

    counts = {"dry_run": 0, "ingested": 0, "duplicate": 0, "skipped": 0, "failed": 0}
    for candidate in candidates:
        try:
            result = ingest_candidate(candidate, write=args.write)
            counts[result["status"]] += 1
            print(f'{result["status"].upper()}: {result["reference"] or "(no reference)"} — {result["title"]}')
            print(f'  {result["reason"]}')
        except Exception as exc:
            counts["failed"] += 1
            print(f"FAILED: {candidate.reference or candidate.source_url} — {exc}", file=sys.stderr)
    print(f"\nSummary ({'write enabled' if args.write else 'dry-run'}): {counts}")
    return 1 if counts["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
