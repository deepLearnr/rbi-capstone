from pydantic import BaseModel, ConfigDict


class DocumentChunkCreate(BaseModel):
    chunk_index: int
    content: str
    page_start: int | None = None
    page_end: int | None = None
    section_reference: str | None = None
    heading: str | None = None
    heading_path: str | None = None
    metadata: dict | None = None


class DocumentChunkResponse(DocumentChunkCreate):
    id: int
    document_id: int

    model_config = ConfigDict(from_attributes=True)
