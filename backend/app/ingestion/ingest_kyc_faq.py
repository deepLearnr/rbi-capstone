from pathlib import Path

from sqlalchemy import select

from app.db.session import SessionLocal
from app.ingestion.faq_chunker import chunk_faq_pages
from app.ingestion.pdf_extractor import extract_pdf_pages
from app.models.document import Document
from app.models.document_chunk import DocumentChunk


def ingest_kcy_faq(pdf_path: str | Path) -> int:
    pdf_path = Path(pdf_path)

    pages = extract_pdf_pages(pdf_path)
    chunks = chunk_faq_pages(pages)

    with SessionLocal() as db:
        existing = db.scalar(
            select(Document).where(
                Document.source_file == pdf_path.name
            )
        )

        if existing:
            raise RuntimeError(
                f"Document already exists: {existing.id} "
                f"({existing.source_file})"
            )

        document = Document(
            title="FAQs on Master Direction on KYC dated February 25, 2016",
            document_type="faq",
            rbi_reference="Master Direction on KYC",
            publication_date=None,
            department=None,
            source_url=None,
            source_file=pdf_path.name,
            language="en",
            description=(
                "FAQs on Master Direction on KYC dated "
                "February 25, 2016 (June 9, 2025)."
            ),
        )

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
                    section_reference=f"Q{chunk.question_number}",
                    heading=chunk.heading,
                    heading_path=chunk.heading,
                    chunk_metadata=chunk.metadata,
                )
            )

        db.commit()

        return document.id


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: python -m app.ingestion.ingest_kcy_faq <pdf-path>"
        )

    document_id = ingest_kcy_faq(sys.argv[1])

    print(f"Ingestion complete. Document ID: {document_id}")
