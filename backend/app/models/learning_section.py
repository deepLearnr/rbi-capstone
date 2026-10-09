from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class LearningSection(Base):
    __tablename__ = "learning_sections"

    __table_args__ = (
        UniqueConstraint(
            "module_id",
            "section_order",
            name="uq_learning_section_order",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    module_id: Mapped[int] = mapped_column(
        ForeignKey("learning_modules.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    section_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    module = relationship(
        "LearningModule",
        back_populates="sections",
    )
