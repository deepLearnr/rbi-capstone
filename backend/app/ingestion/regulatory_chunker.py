import re
from dataclasses import dataclass

from app.ingestion.pdf_extractor import ExtractedPage


SECTION_PATTERN = re.compile(
    r"(?m)^\s*(\d+)\.\s+"
)

SIGNATURE_PATTERN = re.compile(
    r"(?m)^\s*\(Veena Srivastava\)\s*$"
)


@dataclass
class RegulatoryChunk:
    chunk_index: int
    content: str
    page_start: int
    page_end: int
    section_reference: str
    heading: str
    heading_path: str
    metadata: dict


def _clean_text(text: str) -> str:
    text = SIGNATURE_PATTERN.sub("", text)

    lines = [line.rstrip() for line in text.splitlines()]

    cleaned: list[str] = []
    previous_blank = False

    for line in lines:
        line = line.strip()

        if not line:
            if not previous_blank:
                cleaned.append("")
            previous_blank = True
            continue

        cleaned.append(line)
        previous_blank = False

    return "\n".join(cleaned).strip()


def _section_heading(section_number: str, section_text: str) -> str:
    """
    Extract a meaningful heading for numbered sections.

    For sections 2 and 4, the first sentence is not actually a heading,
    so use a stable semantic label rather than treating the first sentence
    as the heading.
    """

    if section_number == "2":
        return "Authority for Amendment Directions"

    if section_number == "3":
        return "Short Title and Commencement"

    if section_number == "4":
        return "Modification of KYC Directions"

    match = re.match(
        rf"^\s*{re.escape(section_number)}\.\s+(.+)$",
        section_text,
        flags=re.DOTALL,
    )

    if match:
        first_line = match.group(1).strip().splitlines()[0].strip()

        if len(first_line) <= 120:
            return first_line

    return f"Section {section_number}"


def chunk_regulatory_pages(
    pages: list[ExtractedPage],
) -> list[RegulatoryChunk]:
    """
    Convert a numbered regulatory PDF into provenance-preserving chunks.

    Rules:
    - Preserve preamble text before section 2 as a dedicated Preamble chunk.
    - Split only on numbered top-level sections.
    - Preserve a section across PDF pages when necessary.
    - Keep section 4 and its amended paragraph 5(1)(v) together.
    - Remove the issuer signature from retrieval content.
    """

    chunks: list[RegulatoryChunk] = []

    current_reference: str | None = None
    current_heading: str | None = None
    current_parts: list[str] = []
    current_page_start: int | None = None
    current_page_end: int | None = None

    def flush_current() -> None:
        nonlocal current_reference
        nonlocal current_heading
        nonlocal current_parts
        nonlocal current_page_start
        nonlocal current_page_end

        if (
            current_reference is None
            or current_heading is None
            or not current_parts
            or current_page_start is None
            or current_page_end is None
        ):
            return

        content = _clean_text("\n".join(current_parts))

        if not content:
            return

        chunks.append(
            RegulatoryChunk(
                chunk_index=len(chunks),
                content=content,
                page_start=current_page_start,
                page_end=current_page_end,
                section_reference=current_reference,
                heading=current_heading,
                heading_path=current_heading,
                metadata={
                    "content_type": "regulatory",
                    "section_reference": current_reference,
                },
            )
        )

    def start_chunk(
        reference: str,
        heading: str,
        content: str,
        page_number: int,
    ) -> None:
        nonlocal current_reference
        nonlocal current_heading
        nonlocal current_parts
        nonlocal current_page_start
        nonlocal current_page_end

        current_reference = reference
        current_heading = heading
        current_parts = [content]
        current_page_start = page_number
        current_page_end = page_number

    for page in pages:
        text = page.text.strip()

        if not text:
            continue

        matches = list(SECTION_PATTERN.finditer(text))

        # No numbered section on this page.
        if not matches:
            if current_reference is not None:
                current_parts.append(text)
                current_page_end = page.page_number
            continue

        # Preserve everything before the first numbered section.
        prefix = text[:matches[0].start()].strip()

        if prefix:
            if current_reference is None:
                start_chunk(
                    reference="Preamble",
                    heading="Amendment Overview",
                    content=prefix,
                    page_number=page.page_number,
                )
            else:
                current_parts.append(prefix)
                current_page_end = page.page_number

        for index, match in enumerate(matches):
            section_number = match.group(1)

            start = match.start()
            end = (
                matches[index + 1].start()
                if index + 1 < len(matches)
                else len(text)
            )

            section_text = text[start:end].strip()

            if current_reference is not None:
                flush_current()

            start_chunk(
                reference=section_number,
                heading=_section_heading(section_number, section_text),
                content=section_text,
                page_number=page.page_number,
            )

    flush_current()

    return chunks
