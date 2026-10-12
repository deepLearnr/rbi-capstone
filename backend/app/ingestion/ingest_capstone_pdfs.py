"""Dry-run-first ingestion for the remaining required RBI capstone PDFs.

Run from backend/: python -m app.ingestion.ingest_capstone_pdfs
Persist only after reviewing the manifest and dry-run: add --write.
PDF embeddings are generated afterward with app.embeddings.embed_documents.
"""

from __future__ import annotations

import argparse
import hashlib
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from sqlalchemy import func, or_, select

from app.db.session import SessionLocal
from app.ingestion.pdf_extractor import extract_pdf_pages
from app.models.document import Document
from app.models.document_chunk import DocumentChunk

BACKEND_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BACKEND_DIR.parent / "data" / "raw"
MAX_CHARS = 1_700
OVERLAP_CHARS = 180


@dataclass(frozen=True)
class PDFSpec:
    filename: str
    title: str
    document_type: str
    rbi_reference: str | None
    publication_date: date | None
    department: str | None
    source_url: str
    description: str
    regulatory_status: str
    content_type: str


# These are the three PDF sources from the capstone brief that were present
# locally but are not yet in the fresh Supabase database. The urban-named
# file was mislabelled on disk; the apply instructions safely rename it first.
PDF_SPECS: tuple[PDFSpec, ...] = (
    PDFSpec(
        filename="core_principles_effective_banking_supervision_1999.pdf",
        title="Core Principles of Effective Banking Supervision",
        document_type="reference_document",
        rbi_reference=None,
        publication_date=None,  # RBI source identifies October 1999, not a day.
        department="Department of Banking Supervision",
        source_url="https://rbi.org.in/upload/publications/pdfs/10115.pdf",
        description=(
            "RBI publication from October 1999 presenting the Indian position. "
            "Historical reference only; not a statement of current regulatory requirements."
        ),
        regulatory_status="historical",
        content_type="reference",
    ),
    PDFSpec(
        filename="RBI_kyc-2.pdf",
        title="Master Circular on Maintenance of Deposit Accounts – Primary (Urban) Co-operative Banks",
        document_type="master_circular",
        rbi_reference="RBI/2015-16/5",
        publication_date=date(2015, 7, 1),
        department="Department of Co-operative Bank Regulation",
        source_url=(
            "https://www.rbi.org.in/commonman/Upload/English/Notification/PDFs/"
            "05MD17E67B8A6F93462CAEA7C2E30B27C653.pdf"
        ),
        description=(
            "Master Circular issued July 1, 2015, consolidating instructions up to "
            "June 30, 2015. Historical edition; verify later RBI instructions before "
            "treating any provision as currently applicable."
        ),
        regulatory_status="historical",
        content_type="regulatory",
    ),
    PDFSpec(
        filename="RBI_KYC.pdf",
        title="FAQs on Master Direction on KYC dated February 25, 2016 (June 9, 2025)",
        document_type="faq",
        rbi_reference=None,
        publication_date=date(2025, 6, 9),
        department="Commercial Banking",
        source_url="https://www.rbi.org.in/commonperson/english/Scripts/FAQs.aspx?Id=3782",
        description=(
            "RBI KYC FAQ page dated June 9, 2025. Newer KYC amendment directions "
            "were issued in September 2026, so this FAQ's currentness has not been "
            "verified against those later amendments; do not use it alone to assert "
            "current applicability."
        ),
        regulatory_status="currentness_unverified",
        content_type="faq",
    ),
)


@dataclass(frozen=True)
class ExistingHTMLRepair:
    source_url_fragment: str
    source_url: str
    title: str
    document_type: str
    rbi_reference: str
    publication_date: date
    department: str
    description: str
    regulatory_status: str


# The discovery pipeline extracted the RBI page heading as the generic title
# "Master Directions". These canonical titles and references improve citations.
EXISTING_HTML_REPAIRS: tuple[ExistingHTMLRepair, ...] = (
    ExistingHTMLRepair(
        source_url_fragment="BS_ViewMasDirections.aspx?id=12818",
        source_url="https://www.rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=12818",
        title="Master Direction – Facility for Exchange of Notes and Coins",
        document_type="master_direction",
        rbi_reference="RBI/2025-26/133",
        publication_date=date(2025, 4, 1),
        department="Department of Currency Management",
        description=(
            "Official RBI Master Direction dated April 1, 2025. Check for later "
            "RBI amendments before relying on a provision for current applicability."
        ),
        regulatory_status="active",
    ),
    ExistingHTMLRepair(
        source_url_fragment="NotificationUser.aspx?Id=12848",
        source_url="https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=12848",
        title="Reserve Bank of India (Digital Lending) Directions, 2025",
        document_type="regulatory_direction",
        rbi_reference="RBI/2025-26/36",
        publication_date=date(2025, 5, 8),
        department="Department of Regulation",
        description=(
            "Official RBI Digital Lending Directions, 2025, issued May 8, 2025. "
            "Check for later RBI amendments before relying on a provision for current applicability."
        ),
        regulatory_status="active",
    ),
)


def _content_hash(content: str) -> str:
    normalized = re.sub(r"\s+", " ", content).strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _chunks_for_page(text: str, page_number: int, next_index: int, spec: PDFSpec) -> list[dict[str, Any]]:
    text = "\n".join(line.rstrip() for line in text.splitlines()).strip()
    if not text:
        return []

    chunks: list[dict[str, Any]] = []
    start = 0
    while start < len(text):
        end = min(start + MAX_CHARS, len(text))
        if end < len(text):
            lower_bound = start + int(MAX_CHARS * 0.55)
            candidates = [
                text.rfind("\n\n", lower_bound, end),
                text.rfind("\n", lower_bound, end),
                text.rfind(". ", lower_bound, end),
                text.rfind(" ", lower_bound, end),
            ]
            cut = max(candidates)
            if cut > lower_bound:
                end = cut + (1 if text[cut:cut + 1] == " " else 0)

        content = text[start:end].strip()
        if content:
            first_line = next(
                (line.strip() for line in content.splitlines() if line.strip()),
                f"Page {page_number}",
            )
            heading = first_line[:160]
            chunks.append(
                {
                    "chunk_index": next_index + len(chunks),
                    "content": content,
                    "page_start": page_number,
                    "page_end": page_number,
                    "section_reference": f"Page {page_number}",
                    "heading": heading,
                    "heading_path": heading,
                    "metadata": {
                        "content_type": spec.content_type,
                        "source_file": spec.filename,
                        "source_url": spec.source_url,
                        "regulatory_status": spec.regulatory_status,
                        "publication_date": (
                            spec.publication_date.isoformat()
                            if spec.publication_date
                            else None
                        ),
                    },
                }
            )

        if end >= len(text):
            break
        start = max(start + 1, end - OVERLAP_CHARS)

    return chunks


def prepare_document(spec: PDFSpec) -> tuple[Path, list[dict[str, Any]], int]:
    path = RAW_DIR / spec.filename
    if not path.is_file():
        raise FileNotFoundError(
            f"Required PDF not found: {path}. Check the source file name before writing."
        )

    pages = extract_pdf_pages(path)
    extracted_chars = sum(len(page.text.strip()) for page in pages)
    if extracted_chars < 300:
        raise ValueError(
            f"Only {extracted_chars} characters extracted from {spec.filename}; "
            "refusing to ingest a potentially scanned/empty PDF."
        )

    chunks: list[dict[str, Any]] = []
    for page in pages:
        chunks.extend(_chunks_for_page(page.text, page.page_number, len(chunks), spec))

    if not chunks:
        raise ValueError(f"No non-empty chunks extracted from {spec.filename}.")

    for chunk in chunks:
        if not chunk["content"].strip():
            raise ValueError(f"Empty chunk generated for {spec.filename}.")

    return path, chunks, extracted_chars


def persist_document(spec: PDFSpec, chunks: list[dict[str, Any]]) -> str:
    with SessionLocal() as db:
        existing = db.scalar(
            select(Document).where(
                or_(
                    Document.source_file == spec.filename,
                    Document.source_url == spec.source_url,
                )
            )
        )
        if existing is not None:
            return f"SKIPPED_DUPLICATE: document_id={existing.id}, source_file={existing.source_file}"

        try:
            document = Document(
                title=spec.title,
                document_type=spec.document_type,
                rbi_reference=spec.rbi_reference,
                publication_date=spec.publication_date,
                department=spec.department,
                source_url=spec.source_url,
                source_file=spec.filename,
                language="en",
                description=spec.description,
            )
            db.add(document)
            db.flush()

            for chunk in chunks:
                db.add(
                    DocumentChunk(
                        document_id=document.id,
                        chunk_index=chunk["chunk_index"],
                        content=chunk["content"],
                        page_start=chunk["page_start"],
                        page_end=chunk["page_end"],
                        section_reference=chunk["section_reference"],
                        heading=chunk["heading"],
                        heading_path=chunk["heading_path"],
                        chunk_metadata=chunk["metadata"],
                        content_hash=_content_hash(chunk["content"]),
                    )
                )

            db.commit()
            return f"INGESTED: document_id={document.id}, chunks={len(chunks)}"
        except Exception:
            db.rollback()
            raise


def repair_existing_html_metadata(*, write: bool) -> tuple[int, int]:
    """Preview/apply canonical metadata to the two already-ingested RBI pages."""
    repaired = 0
    missing = 0
    with SessionLocal() as db:
        for spec in EXISTING_HTML_REPAIRS:
            document = db.scalar(
                select(Document).where(
                    func.lower(Document.source_url).contains(
                        spec.source_url_fragment.lower()
                    )
                )
            )
            if document is None:
                missing += 1
                print(f"METADATA_NOT_FOUND: {spec.title}")
                continue

            print(
                f"METADATA {'UPDATE' if write else 'DRY RUN'}: "
                f"document_id={document.id}; "
                f"title {document.title!r} -> {spec.title!r}; "
                f"reference={spec.rbi_reference}"
            )
            if not write:
                continue

            document.title = spec.title
            document.document_type = spec.document_type
            document.rbi_reference = spec.rbi_reference
            document.publication_date = spec.publication_date
            document.department = spec.department
            document.source_url = spec.source_url
            document.description = spec.description

            chunks = db.scalars(
                select(DocumentChunk).where(
                    DocumentChunk.document_id == document.id
                )
            ).all()
            for chunk in chunks:
                metadata = dict(chunk.chunk_metadata or {})
                metadata.update(
                    {
                        "source_file": document.source_file,
                        "source_url": spec.source_url,
                        "rbi_reference": spec.rbi_reference,
                        "publication_date": spec.publication_date.isoformat(),
                        "regulatory_status": spec.regulatory_status,
                    }
                )
                chunk.chunk_metadata = metadata
            db.commit()
            repaired += 1

    return repaired, missing


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Ingest the remaining required capstone RBI PDFs and repair titles "
            "for two previously ingested RBI HTML sources (dry-run by default)."
        )
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Persist prepared documents/chunks and apply canonical metadata repairs.",
    )
    args = parser.parse_args()

    mode = "WRITE ENABLED" if args.write else "DRY RUN"
    print(f"Mode: {mode}")
    failures = 0
    prepared: list[tuple[PDFSpec, list[dict[str, Any]], int]] = []

    for spec in PDF_SPECS:
        try:
            _path, chunks, char_count = prepare_document(spec)
            prepared.append((spec, chunks, char_count))
            print(f"\n{mode}: {spec.title}")
            print(f"  file: {spec.filename}")
            print(f"  RBI reference: {spec.rbi_reference or '(none)'}")
            print(
                "  publication date: "
                f"{spec.publication_date or '(month/year only or not available)'}"
            )
            print(f"  regulatory status: {spec.regulatory_status}")
            print(f"  official source: {spec.source_url}")
            print(f"  extracted characters: {char_count}")
            print(f"  chunks prepared: {len(chunks)}")
        except Exception as exc:
            failures += 1
            print(f"FAILED: {spec.filename}: {type(exc).__name__}: {exc}")

    # Persist all successfully prepared PDFs only when explicitly requested.
    if args.write:
        for spec, chunks, _char_count in prepared:
            try:
                print(f"  {persist_document(spec, chunks)}")
            except Exception as exc:
                failures += 1
                print(f"FAILED_TO_WRITE: {spec.filename}: {type(exc).__name__}: {exc}")

    try:
        _repaired, missing = repair_existing_html_metadata(write=args.write)
        if missing:
            print(
                f"WARNING: {missing} expected HTML document(s) were not found; "
                "they were not modified."
            )
    except Exception as exc:
        failures += 1
        print(f"METADATA_REPAIR_FAILED: {type(exc).__name__}: {exc}")

    print(
        f"\nSummary: prepared={len(prepared)}/{len(PDF_SPECS)}, "
        f"failures={failures}, write={args.write}"
    )
    if args.write and failures == 0:
        print(
            "Next: run python -m app.embeddings.embed_documents once to embed "
            "newly inserted PDF chunks."
        )
    else:
        print("No PDF writes or metadata changes were made in dry-run mode." if not args.write else "Review failures above before embedding.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
