import argparse
from datetime import date
from pathlib import Path

from sqlalchemy import select

from app.db.session import SessionLocal
from app.ingestion.pdf_extractor import extract_pdf_pages
from app.ingestion.regulatory_chunker import chunk_regulatory_pages
from app.models.document import Document
from app.models.document_chunk import DocumentChunk


TITLE = (
    "Reserve Bank of India (Commercial Banks – Know Your Customer) "
    "Amendment Directions, 2026"
)

DOCUMENT_TYPE = "regulatory_direction"
RBI_REFERENCE = "RBI/2026-27/257"
PUBLICATION_DATE = date(2026, 9, 18)
DEPARTMENT = "Department of Regulation"
LANGUAGE = "en"

DESCRIPTION = (
    "Reserve Bank of India (Commercial Banks – Know Your Customer) "
    "Amendment Directions, 2026"
)


def build_regulatory_document(
    pdf_path: str | Path,
    *,
    source_url: str | None = None,
):
    pdf_path = Path(pdf_path)

    pages = extract_pdf_pages(pdf_path)
    chunks = chunk_regulatory_pages(pages)

    document_data = {
        "title": TITLE,
        "document_type": DOCUMENT_TYPE,
        "rbi_reference": RBI_REFERENCE,
        "publication_date": PUBLICATION_DATE,
        "department": DEPARTMENT,
        "source_url": source_url,
        "source_file": pdf_path.name,
        "language": LANGUAGE,
        "description": DESCRIPTION,
    }

    return document_data, chunks


def ingest_regulatory_pdf(
    pdf_path: str | Path,
    *,
    source_url: str | None = None,
    dry_run: bool = False,
):
    pdf_path = Path(pdf_path)

    document_data, chunks = build_regulatory_document(
        pdf_path, source_url=source_url
    )

    print("Document")
    print(f"  title: {document_data['title']}")
    print(f"  type: {document_data['document_type']}")
    print(f"  RBI reference: {document_data['rbi_reference']}")
    print(f"  publication date: {document_data['publication_date']}")
    print(f"  source file: {document_data['source_file']}")
    print(f"  source URL: {document_data['source_url'] or 'UNVERIFIED / NOT SET'}")
    print(f"  chunks: {len(chunks)}")

    if dry_run:
        print("\nDRY RUN — no database changes")

        for chunk in chunks:
            print("\n" + "=" * 80)
            print(
                f"CHUNK {chunk.chunk_index} | "
                f"{chunk.section_reference} | "
                f"pages {chunk.page_start}-{chunk.page_end}"
            )
            print("=" * 80)
            print(f"heading: {chunk.heading}")
            print(chunk.content)

        return None

    with SessionLocal() as db:
        existing = db.scalar(
            select(Document).where(
                Document.source_file == pdf_path.name
            )
        )

        if existing is not None:
            raise RuntimeError(
                f"Document already exists: "
                f"{existing.id} ({existing.source_file})"
            )

        document = Document(**document_data)

        db.add(document)
        db.flush()

        for chunk in chunks:
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
                    chunk_metadata=chunk.metadata,
                )
            )

        db.commit()

        print(f"\nInserted document ID: {document.id}")
        print(f"Inserted chunks: {len(chunks)}")

        return document.id


def main():
    parser = argparse.ArgumentParser(
        description="Ingest a regulatory RBI PDF."
    )

    parser.add_argument("pdf_path")
    parser.add_argument(
        "--source-url",
        default=None,
        help="Verified official RBI source URL for this PDF.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Inspect parsed chunks without writing to PostgreSQL.",
    )

    args = parser.parse_args()

    ingest_regulatory_pdf(
        args.pdf_path,
        source_url=args.source_url,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
