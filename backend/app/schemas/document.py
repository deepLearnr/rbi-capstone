from datetime import date

from pydantic import BaseModel, ConfigDict, HttpUrl


class DocumentCreate(BaseModel):
    title: str
    document_type: str
    rbi_reference: str | None = None
    publication_date: date | None = None
    department: str | None = None
    source_url: HttpUrl | None = None
    source_file: str | None = None
    language: str = "en"
    description: str | None = None


class DocumentResponse(DocumentCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)
