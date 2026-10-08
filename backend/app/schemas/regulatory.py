from datetime import date

from pydantic import BaseModel, ConfigDict


class TerminologyItemResponse(BaseModel):
    term: str
    meaning: str


class RegulatorySimplificationResponse(BaseModel):
    executive_summary: str
    what_changed: str
    why_it_matters: str
    who_is_affected: list[str]
    what_should_i_do: list[str]
    important_dates: list[str]
    terminology: list[TerminologyItemResponse]


class RegulatoryDocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    rbi_reference: str | None = None
    source_file: str | None = None
    source_url: str | None = None


class RegulatoryUpdateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    document_id: int
    title: str
    category: str
    publication_date: date | None
    effective_date: date | None
    importance: str | None
    simplification: RegulatorySimplificationResponse
    document: RegulatoryDocumentResponse