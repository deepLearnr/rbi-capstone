from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class LearningModule(Base):
    __tablename__ = "learning_modules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    document_id: Mapped[int | None] = mapped_column(
        ForeignKey("documents.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    regulatory_update_id: Mapped[int | None] = mapped_column(
        ForeignKey("regulatory_updates.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    difficulty: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="beginner",
    )
    estimated_minutes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="published",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    document = relationship("Document", lazy="joined")
    regulatory_update = relationship("RegulatoryUpdate", lazy="joined")

    sections = relationship(
        "LearningSection",
        back_populates="module",
        cascade="all, delete-orphan",
        order_by="LearningSection.section_order",
    )

    scenarios = relationship(
        "Scenario",
        back_populates="module",
        cascade="all, delete-orphan",
    )

    assessments = relationship(
        "Assessment",
        back_populates="module",
        cascade="all, delete-orphan",
    )

    progress_records = relationship(
        "LearningProgress",
        back_populates="module",
        cascade="all, delete-orphan",
    )
