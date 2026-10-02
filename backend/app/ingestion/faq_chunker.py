import re
from dataclasses import dataclass

from app.ingestion.pdf_extractor import ExtractedPage


QUESTION_PATTERN = re.compile(
    r"(?m)^\s*Q\s*(\d+)\s*\.\s*"
)


@dataclass
class FAQChunk:
    chunk_index: int
    question_number: str
    content: str
    page_start: int
    page_end: int
    heading: str | None = None
    metadata: dict | None = None


def chunk_faq_pages(
    pages: list[ExtractedPage],
) -> list[FAQChunk]:
    """
    Convert page-level FAQ text into question-level chunks.

    A question may span multiple PDF pages. In that case,
    page_start/page_end preserve the complete provenance.
    """

    chunks: list[FAQChunk] = []

    current_question: str | None = None
    current_parts: list[str] = []
    current_page_start: int | None = None
    current_page_end: int | None = None

    def flush_current() -> None:
        nonlocal current_question
        nonlocal current_parts
        nonlocal current_page_start
        nonlocal current_page_end

        if (
            current_question is None
            or not current_parts
            or current_page_start is None
            or current_page_end is None
        ):
            return

        content = "\n".join(current_parts).strip()

        if not content:
            return

        chunks.append(
            FAQChunk(
                chunk_index=len(chunks),
                question_number=current_question,
                content=content,
                page_start=current_page_start,
                page_end=current_page_end,
                heading=f"Q{current_question}",
                metadata={
                    "content_type": "faq",
                    "question_number": current_question,
                },
            )
        )

    for page in pages:
        text = page.text.strip()

        if not text:
            continue

        matches = list(QUESTION_PATTERN.finditer(text))

        # This page contains no new question.
        # It is therefore continuation text for the current question.
        if not matches:
            if current_question is not None:
                current_parts.append(text)
                current_page_end = page.page_number

            continue

        for index, match in enumerate(matches):
            question_number = match.group(1)

            start = match.start()
            end = (
                matches[index + 1].start()
                if index + 1 < len(matches)
                else len(text)
            )

            question_text = text[start:end].strip()

            # If another question was already active, this new
            # question begins on the current page. Therefore the
            # previous question definitely extends through this page.
            if current_question is not None:
                current_page_end = page.page_number
                flush_current()

            current_question = question_number
            current_parts = [question_text]
            current_page_start = page.page_number
            current_page_end = page.page_number

    flush_current()

    return chunks
