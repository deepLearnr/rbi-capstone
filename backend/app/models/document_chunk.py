from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from app.db.session import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    __table_args__ = (
    	UniqueConstraint(
        	"document_id",
        	"chunk_index",
        	name="uq_document_chunk_index",
       	),
    ) 

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    page_start: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    page_end: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    section_reference: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    heading: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    heading_path: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )


    chunk_metadata: Mapped[dict | None] = mapped_column(
        "metadata",
        JSON,
        nullable=True,
    )


    content_hash: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        index=True,
    )

    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(384),
        nullable=True,
    )

    embedding_model: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    document = relationship(
        "Document",
        back_populates="chunks",
    )
