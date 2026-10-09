import re
from dataclasses import dataclass

from app.ingestion.pdf_extractor import ExtractedPage
from app.ingestion.schemas import IngestionChunk


@dataclass
class UCBCyberChunk:
    chunk_index: int
    content: str
    page_start: int
    page_end: int
    section_reference: str | None = None
    heading: str | None = None


# Main circular paragraphs, e.g. "2. Please refer to our Circular..."
MAIN_PARAGRAPH_PATTERN = re.compile(
    r"^\s*([2-8])\.\s+(.+)$"
)

# Annex section headings, e.g. "1. Network Management and Security" or "3. Application Security Life Cycle (ASLC)3".
# Decimal controls such as 1.1. are deliberately excluded.
ANNEX_HEADING_PATTERN = re.compile(
    r"^\s*(\d{1,2})\.\s+([A-Z][A-Za-z /(),&'–—-]{3,100})\s*\d*\s*$"
)

# Sub-headings inside Annex IV, Section 6 (IT & IS Governance Framework)
GOVERNANCE_SUBHEADINGS = [
    "IT Strategy Committee",
    "IT Steering Committee",
    "Information Security Committee",
    "Chief Information Security Officer (CISO)",
    "Cyber Security Team/Function",
    "Audit Committee of Board (ACB)",
]

GOVERNANCE_SUBHEADING_PATTERN = re.compile(
    r"^\s*(?:\d+\.\d+\s+)?(" + "|".join(re.escape(h) for h in GOVERNANCE_SUBHEADINGS) + r")\s*$",
    re.IGNORECASE,
)

KNOWN_ANNEX_HEADINGS = {
    "network management and security",
    "secure configuration",
    "application security life cycle (aslc)",
    "change management",
    "periodic testing",
    "user access control / management",
    "user access control",
    "authentication framework for customers",
    "anti-phishing",
    "data leak prevention strategy",
    "audit logs",
    "incident response and management",
    "advanced real-time threat defence and management",
    "maintenance, monitoring, and analysis of audit logs",
    "user / employee/ management awareness",
    "risk based transaction monitoring",
    "participation in cyber drills",
    "forensics and metrics",
    "it strategy and policy",
    "it and is governance framework",
    "arrangement for continuous surveillance - setting up of cyber security operation",
}


def _clean_line(line: str) -> str:
    """Remove obvious extraction noise without rewriting source content."""
    line = line.replace("\x00", " ")
    line = re.sub(r"[ \t]+", " ", line)
    return line.strip()


def _is_noise(line: str) -> bool:
    normalized = re.sub(r"\s+", " ", line).strip().lower()

    if normalized == "withdrawn":
        return True

    if re.fullmatch(r"(?:page\s*)?\d{1,3}", normalized):
        return True
    if re.fullmatch(r"[ivxlcdm]{1,8}", normalized):
        return True

    return False


def _detect_annex_start(page_text: str) -> tuple[str, str] | None:
    """Return an annex only when its actual heading and title are present."""
    lines = [
        " ".join(line.split())
        for line in page_text.splitlines()
        if line.strip()
    ]
    for index, line in enumerate(lines):
        match = re.fullmatch(
            r"Annex\s*[-–—]?\s*(IV|III|II|I)",
            line,
            re.IGNORECASE,
        )
        if not match:
            continue
        following_text = " ".join(lines[index + 1:index + 5]).lower()
        if "baseline cyber security" in following_text:
            return match.group(1).upper(), line
    return None


def _heading_from_annex_line(line: str) -> tuple[str, str] | None:
    match = ANNEX_HEADING_PATTERN.match(line)
    if not match:
        return None

    number, title = match.groups()
    normalized_title = re.sub(r"\s+", " ", title).strip().lower()

    if normalized_title not in KNOWN_ANNEX_HEADINGS:
        return None

    return number, title.strip()


def _make_chunk(
    index: int,
    lines: list[tuple[int, str]],
    section_reference: str | None,
    heading: str | None,
) -> UCBCyberChunk | None:
    content = "\n".join(line for _, line in lines).strip()
    if not content:
        return None

    pages = [page_number for page_number, _ in lines]
    return UCBCyberChunk(
        chunk_index=index,
        content=content,
        page_start=min(pages),
        page_end=max(pages),
        section_reference=section_reference,
        heading=heading,
    )


def chunk_ucb_cyber_pages(
    pages: list[ExtractedPage],
) -> list[UCBCyberChunk]:
    chunks: list[UCBCyberChunk] = []
    current_lines: list[tuple[int, str]] = []
    current_reference: str | None = "Preamble"
    current_heading: str | None = "Circular Overview"
    active_annex: str | None = None

    def flush() -> None:
        nonlocal current_lines
        chunk = _make_chunk(
            index=len(chunks),
            lines=current_lines,
            section_reference=current_reference,
            heading=current_heading,
        )
        if chunk is not None:
            chunks.append(chunk)
        current_lines = []

    for page in pages:
        # Detect page-level Annex header before processing lines
        annex_start = _detect_annex_start(page.text)
        if annex_start:
            annex_num, annex_line = annex_start
            flush()
            active_annex = f"Annex {annex_num}"
            current_reference = active_annex
            current_heading = annex_line

        for raw_line in page.text.splitlines():
            line = _clean_line(raw_line)
            if not line or _is_noise(line):
                continue

            # Section headings inside Annexes
            if active_annex is not None:
                heading_match = _heading_from_annex_line(line)
                if heading_match:
                    section_number, section_title = heading_match
                    flush()
                    current_reference = (
                        f"{active_annex}, Section {section_number}"
                    )
                    current_heading = section_title
                    current_lines.append((page.page_number, line))
                    continue

                # Sub-headings inside Annex IV Section 6
                if active_annex == "Annex IV" and current_reference and "Section 6" in current_reference:
                    sub_match = GOVERNANCE_SUBHEADING_PATTERN.match(line)
                    if sub_match:
                        sub_title = sub_match.group(1).strip()
                        flush()
                        current_reference = "Annex IV, Section 6"
                        current_heading = f"IT and IS Governance Framework - {sub_title}"
                        current_lines.append((page.page_number, line))
                        continue

            # Before active annex: handle circular paragraphs, closing, policy extract, and framework intro
            if active_annex is None:
                lower_line = line.lower()

                # 1. Circular Closing sign-off
                if lower_line.startswith("yours faithfully") or lower_line.startswith("yours sincerely"):
                    flush()
                    current_reference = "Circular Closing"
                    current_heading = "Circular Sign-off"
                    current_lines.append((page.page_number, line))
                    continue

                # 2. Footnote detection following Circular Closing
                if (
                    current_reference == "Circular Closing"
                    and re.match(
                        r"^\s*\d+\s+Risk Based Transaction Monitoring",
                        line,
                        re.IGNORECASE,
                    )
                ):
                    flush()
                    current_reference = "Circular Footnote"
                    current_heading = "Risk Based Transaction Monitoring Footnote"
                    current_lines.append((page.page_number, line))
                    continue

                # 3. Extract from Monetary Policy Statement
                if lower_line.startswith("extract from the fifth bi-monthly monetary policy statement"):
                    flush()
                    current_reference = "Referenced Policy Extract"
                    current_heading = "Monetary Policy Statement Extract"
                    current_lines.append((page.page_number, line))
                    continue

                # 4. Numbered framework heading marks the end of the monetary-policy extract
                if (
                    current_reference == "Referenced Policy Extract"
                    and re.match(
                        r"^\s*3\.\s+Comprehensive Cyber Security Framework",
                        line,
                        re.IGNORECASE,
                    )
                ):
                    flush()
                    current_reference = "Framework Introduction"
                    current_heading = "Comprehensive Cyber Security Framework"
                    current_lines.append((page.page_number, line))
                    continue

                # 5. Generic Framework Introduction fallback
                if (
                    "comprehensive cyber security framework for primary" in lower_line
                    and "graded approach" in lower_line
                    and current_reference != "Framework Introduction"
                ):
                    flush()
                    current_reference = "Framework Introduction"
                    current_heading = "Comprehensive Cyber Security Framework"
                    current_lines.append((page.page_number, line))
                    continue

                # 6. Circular paragraphs 2-8 (restricted to pages 1 and 2)
                paragraph_match = MAIN_PARAGRAPH_PATTERN.match(line)
                if paragraph_match and page.page_number <= 2:
                    paragraph_number = paragraph_match.group(1)
                    paragraph_text = paragraph_match.group(2)
                    flush()
                    current_reference = f"Paragraph {paragraph_number}"
                    current_heading = paragraph_text[:140]
                    current_lines.append((page.page_number, line))
                    continue

            current_lines.append((page.page_number, line))

    flush()

    for index, chunk in enumerate(chunks):
        chunk.chunk_index = index

    return chunks


def normalize_ucb_chunks(chunks: list[UCBCyberChunk]) -> list[IngestionChunk]:
    return [
        IngestionChunk(
            chunk_index=chunk.chunk_index,
            content=chunk.content,
            page_start=chunk.page_start,
            page_end=chunk.page_end,
            section_reference=chunk.section_reference,
            heading=chunk.heading,
            heading_path=chunk.section_reference,
            metadata={
                "source_type": "historical_rbi_circular",
                "regulatory_status": "withdrawn",
            },
        )
        for chunk in chunks
    ]