import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from sqlalchemy import select

from app.db.session import SessionLocal
from app.ingestion.profiles import DocumentProfile
from app.ingestion.schemas import IngestionChunk
from app.models.document import Document
from app.models.document_chunk import DocumentChunk


@dataclass(frozen=True)
class IngestionResult:
    source_file: str
    chunk_count: int
    document_id: int | None
    dry_run: bool


def _content_hash(content: str) -> str:
    normalized = re.sub(r"\s+", " ", content).strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def validate_chunks(
    chunks: list[IngestionChunk],
    *,
    page_count: int | None = None,
) -> None:
    if not chunks:
        raise ValueError("No chunks were produced; refusing ingestion.")

    seen_indices = set()

    for position, chunk in enumerate(chunks):
        if chunk.chunk_index in seen_indices:
            raise ValueError(
                f"Duplicate chunk index: {chunk.chunk_index}"
            )
        seen_indices.add(chunk.chunk_index)

        if chunk.chunk_index != position:
            raise ValueError(
                "Chunk indices must be sequential from zero. "
                f"Expected {position}, got {chunk.chunk_index}."
            )

        if not chunk.content or not chunk.content.strip():
            raise ValueError(
                f"Chunk {chunk.chunk_index} has empty content."
            )

        if chunk.page_start < 1 or chunk.page_end < chunk.page_start:
            raise ValueError(
                f"Chunk {chunk.chunk_index} has invalid page range "
                f"{chunk.page_start}-{chunk.page_end}."
            )

        if page_count is not None and chunk.page_end > page_count:
            raise ValueError(
                f"Chunk {chunk.chunk_index} ends on page "
                f"{chunk.page_end}, but the PDF has {page_count} pages."
            )


def persist_document(
    pdf_path: str | Path,
    profile: DocumentProfile,
    chunks: Iterable[IngestionChunk],
    *,
    dry_run: bool = False,
    page_count: int | None = None,
    source_url: str | None = None,
) -> IngestionResult:
    pdf_path = Path(pdf_path)
    source_file = pdf_path.name
    normalized_chunks = list(chunks)

    if source_file != profile.source_file:
        raise ValueError(
            f"Profile source_file is {profile.source_file!r}, "
            f"but the supplied PDF is {source_file!r}."
        )

    validate_chunks(normalized_chunks, page_count=page_count)

    print(f"Source file: {source_file}")
    print(f"Title: {profile.title}")
    print(f"RBI reference: {profile.rbi_reference}")
    print(f"Regulatory status: {profile.regulatory_status}")
    print(f"Chunks validated: {len(normalized_chunks)}")

    if dry_run:
        print("DRY RUN: no database changes made.")
        return IngestionResult(
            source_file=source_file,
            chunk_count=len(normalized_chunks),
            document_id=None,
            dry_run=True,
        )

    with SessionLocal() as db:
        try:
            existing = db.scalar(
                select(Document).where(
                    Document.source_file == source_file
                )
            )

            if existing is not None:
                raise RuntimeError(
                    f"Document already exists: id={existing.id}, "
                    f"source_file={existing.source_file!r}. "
                    "No changes made."
                )

            document = Document(
                title=profile.title,
                document_type=profile.document_type,
                rbi_reference=profile.rbi_reference,
                publication_date=profile.publication_date,
                department=profile.department,
                source_url=source_url,
                source_file=source_file,
                language=profile.language,
                description=profile.description,
            )

            db.add(document)
            db.flush()

            for chunk in normalized_chunks:
                metadata = dict(chunk.metadata or {})
                metadata.setdefault("source_file", source_file)

                if profile.regulatory_status:
                    metadata["regulatory_status"] = (
                        profile.regulatory_status
                    )

                db.add(
                    DocumentChunk(
                        document_id=document.id,
                        chunk_index=chunk.chunk_index,
                        content=chunk.content,
                        page_start=chunk.page_start,
                        page_end=chunk.page_end,
                        section_reference=chunk.section_reference,
                        heading=chunk.heading,
                        heading_path=chunk.heading_path,
                        chunk_metadata=metadata,
                        content_hash=_content_hash(chunk.content),
                    )
                )

            db.commit()

            document_id = document.id

        except Exception:
            db.rollback()
            raise

    print(f"Inserted document ID: {document_id}")
    print(f"Inserted chunks: {len(normalized_chunks)}")

    return IngestionResult(
        source_file=source_file,
        chunk_count=len(normalized_chunks),
        document_id=document_id,
        dry_run=False,
    )
