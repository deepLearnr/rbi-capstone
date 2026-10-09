from typing import Literal

from pydantic import BaseModel, Field


class SourceCitation(BaseModel):
    chunk_id: int
    document_title: str
    rbi_reference: str | None = None
    source_file: str | None = None
    source_url: str | None = None
    page_start: int | None = None
    page_end: int | None = None
    section: str | None = None
    regulatory_status: str | None = None


class RAGAnswer(BaseModel):
    answer: str
    citations: list[SourceCitation] = Field(default_factory=list)
    evidence_status: Literal["supported", "insufficient"] = "supported"
