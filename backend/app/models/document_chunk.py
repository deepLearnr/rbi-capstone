from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

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

    @property
    def metadata(self) -> dict | None:
        """Provides an alias so Pydantic can fetch this field as 'metadata'"""
        return self.chunk_metadata

    @metadata.setter
    def metadata(self, value: dict | None):
        """Allows assigning values directly to .metadata"""
        self.chunk_metadata = value


    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    document = relationship(
        "Document",
        back_populates="chunks",
    )
