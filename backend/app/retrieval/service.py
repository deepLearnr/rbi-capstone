from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.db.session import SessionLocal
from app.embeddings.service import embed_query
from app.models.document_chunk import DocumentChunk


@dataclass
class RetrievedChunk:
    chunk: DocumentChunk
    document_title: str
    rbi_reference: str | None
    source_url: str | None
    source_file: str | None
    page_start: int | None
    page_end: int | None
    section_reference: str | None
    heading: str | None
    distance: float


def retrieve_chunks(
    query: str,
    top_k: int = 5,
) -> list[RetrievedChunk]:
    query_embedding = embed_query(query)

    with SessionLocal() as session:
        distance = DocumentChunk.embedding.cosine_distance(
            query_embedding
        )

        statement = (
            select(DocumentChunk, distance)
            .options(joinedload(DocumentChunk.document))
            .where(DocumentChunk.embedding.is_not(None))
            .order_by(distance)
            .limit(top_k)
        )

        results = session.execute(statement).all()

        retrieved = []

        for chunk, chunk_distance in results:
            document = chunk.document

            retrieved.append(
                RetrievedChunk(
                    chunk=chunk,
                    document_title=document.title,
                    rbi_reference=document.rbi_reference,
                    source_url=document.source_url,
                    source_file=document.source_file,
                    page_start=chunk.page_start,
                    page_end=chunk.page_end,
                    section_reference=chunk.section_reference,
                    heading=chunk.heading,
                    distance=float(chunk_distance),
                )
            )

        return retrieved
