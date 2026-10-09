from dataclasses import dataclass, field


@dataclass
class IngestionChunk:
    """Common chunk representation for all document chunkers."""

    chunk_index: int
    content: str
    page_start: int
    page_end: int
    section_reference: str | None = None
    heading: str | None = None
    heading_path: str | None = None
    metadata: dict = field(default_factory=dict)
