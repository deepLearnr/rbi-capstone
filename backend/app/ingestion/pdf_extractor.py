from dataclasses import dataclass
from pathlib import Path

import pymupdf


@dataclass
class ExtractedPage:
    page_number: int
    text: str


def extract_pdf_pages(file_path: str | Path) -> list[ExtractedPage]:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    pages: list[ExtractedPage] = []

    with pymupdf.open(path) as document:
        for index, page in enumerate(document):
            text = page.get_text("text").strip()

            pages.append(
                ExtractedPage(
                    page_number=index + 1,
                    text=text,
                )
            )

    return pages
