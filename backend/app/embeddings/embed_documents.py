from sqlalchemy import select

from app.db.session import SessionLocal
from app.embeddings.service import embed_passages
from app.models.document_chunk import DocumentChunk


EMBEDDING_MODEL = "intfloat/multilingual-e5-small"
BATCH_SIZE = 16


def embed_document_chunks() -> None:
    with SessionLocal() as session:
        chunks = session.scalars(
            select(DocumentChunk)
            .where(DocumentChunk.embedding.is_(None))
            .order_by(DocumentChunk.document_id, DocumentChunk.chunk_index)
        ).all()

        print(f"Chunks needing embeddings: {len(chunks)}")

        if not chunks:
            print("Nothing to embed.")
            return

        for start in range(0, len(chunks), BATCH_SIZE):
            batch = chunks[start:start + BATCH_SIZE]

            texts = [chunk.content for chunk in batch]
            embeddings = embed_passages(texts)

            for chunk, embedding in zip(batch, embeddings):
                chunk.embedding = embedding
                chunk.embedding_model = EMBEDDING_MODEL

            session.commit()

            print(
                f"Embedded {min(start + BATCH_SIZE, len(chunks))}"
                f"/{len(chunks)} chunks"
            )


if __name__ == "__main__":
    embed_document_chunks()
