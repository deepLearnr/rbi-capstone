from datetime import date

from pydantic import BaseModel, HttpUrl


class CircularCreate(BaseModel):
    title: str
    circular_number: str | None = None
    department: str | None = None
    publication_date: date | None = None
    source_url: HttpUrl
    document_type: str = "circular"
    language: str = "en"
    content: str


class CircularResponse(CircularCreate):
    id: int