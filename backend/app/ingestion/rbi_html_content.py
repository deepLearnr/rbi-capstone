"""Extract and chunk readable circular content from official RBI HTML pages.

This adapter is intentionally conservative: it starts at the parsed circular
title, stops before the RBI archive/footer, removes script/style/navigation
text, and requires the expected title/reference plus substantial body text.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from html.parser import HTMLParser

from app.ingestion.discover_rbi import Candidate


SKIP_TAGS = {"script", "style", "noscript", "nav", "footer", "header"}
BLOCK_TAGS = {
    "address", "article", "blockquote", "br", "dd", "div", "dl", "dt",
    "h1", "h2", "h3", "h4", "h5", "h6", "li", "ol", "p", "pre",
    "section", "table", "td", "th", "tr", "ul",
}
END_MARKERS = (
    "Archives",
    "More Links",
    "Follow RBI",
    "Back to previous page",
    "Website last updated date",
)
MIN_CONTENT_CHARS = 200
MAX_CHUNK_CHARS = 1800


@dataclass(frozen=True)
class HTMLChunk:
    chunk_index: int
    content: str
    page_start: int | None
    page_end: int | None
    section_reference: str
    heading: str
    heading_path: str
    metadata: dict


class _VisibleTextParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._skip_depth = 0
        self._skip_stack: list[str] = []

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in SKIP_TAGS:
            self._skip_depth += 1
            self._skip_stack.append(tag)
        elif not self._skip_depth and tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_startendtag(self, tag, attrs):
        if tag.lower() in BLOCK_TAGS and not self._skip_depth:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        tag = tag.lower()
        if self._skip_depth:
            # Tags are usually well-formed, but only close the matching ignored
            # element to avoid negative depth on malformed pages.
            if tag in self._skip_stack:
                self._skip_stack.remove(tag)
                self._skip_depth = len(self._skip_stack)
            return
        if tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self._skip_depth and data.strip():
            self.parts.append(data)


def _normalise(text: str) -> str:
    lines = [" ".join(line.split()) for line in text.replace("\xa0", " ").splitlines()]
    lines = [line for line in lines if line]
    return "\n".join(lines)


def _trim_archive_calendar(text: str) -> str:
    """Remove RBI's year/month archive widget, even without a footer label.

    Some circular pages append the archive calendar directly after the
    circular body. Detect its structure instead of relying on a footer string
    or hard-coding the current year.
    """
    lines = text.splitlines()
    month_pattern = re.compile(
        r"^(January|February|March|April|May|June|July|August|September|October|November|December)$",
        re.IGNORECASE,
    )
    for index, line in enumerate(lines):
        if not re.fullmatch(r"(?:19|20)\d{2}", line.strip()):
            continue
        if index + 2 >= len(lines) or lines[index + 1].strip().casefold() != "all months":
            continue
        following = [item.strip() for item in lines[index + 2:index + 7]]
        month_count = sum(bool(month_pattern.fullmatch(item)) for item in following)
        if month_count >= 3:
            return "\n".join(lines[:index]).strip()
    return text


def extract_circular_html_content(html: str, candidate: Candidate) -> str:
    """Return verified circular body text or raise ValueError.

    Content must contain the candidate title and RBI reference, and must be
    long enough to avoid ingesting a redirect shell or page furniture.
    """
    parser = _VisibleTextParser()
    parser.feed(html)
    text = _normalise("\n".join(parser.parts))
    text = _trim_archive_calendar(text)
    title = " ".join((candidate.title or "").split())
    reference = " ".join((candidate.reference or "").split())
    if not title or len(title) < 8 or not reference:
        raise ValueError("Candidate title/reference is missing; refusing HTML ingestion")

    lower = text.casefold()
    title_pos = lower.find(title.casefold())
    if title_pos < 0:
        raise ValueError("Candidate title is not present in the fetched HTML content")
    ref_pos = lower.find(reference.casefold(), title_pos)
    if ref_pos < 0:
        raise ValueError("Candidate RBI reference does not follow its title in the HTML content")

    # The content boundary is the first recognizable archive/footer marker
    # occurring after the reference. Do not use markers that occur before the
    # circular body (e.g. the page heading "Index To RBI Circulars").
    stop_positions = [
        lower.find(marker.casefold(), ref_pos + len(reference))
        for marker in END_MARKERS
    ]
    stop_positions = [position for position in stop_positions if position >= 0]
    end_pos = min(stop_positions) if stop_positions else len(text)
    content = text[title_pos:end_pos].strip()
    if len(content) < MIN_CONTENT_CHARS:
        raise ValueError(
            f"HTML circular body is too short ({len(content)} chars); refusing to ingest page shell"
        )
    if reference.casefold() not in content.casefold():
        raise ValueError("Extracted HTML body lost the expected RBI reference")
    return content


def chunk_html_content(content: str) -> list[HTMLChunk]:
    """Chunk circular text while keeping an attached standalone notification separate.

    RBI circular pages sometimes append a separately numbered notification after
    the circular's enclosure/signature. A standalone ``NOTIFICATION`` line is a
    reliable boundary for this layout. Preserve all text and never fabricate
    PDF page numbers.
    """
    lines = content.splitlines()
    split_at = next(
        (i for i, line in enumerate(lines) if line.strip().casefold() == "notification"),
        None,
    )
    parts: list[tuple[str, str]] = []
    if split_at is not None and split_at > 0 and split_at < len(lines) - 1:
        parts.append(("circular", "\n".join(lines[:split_at]).strip()))
        parts.append(("notification", "\n".join(lines[split_at:]).strip()))
    else:
        parts.append(("circular", content.strip()))

    chunks: list[HTMLChunk] = []

    def split_long_paragraph(paragraph: str) -> list[str]:
        result: list[str] = []
        remainder = paragraph
        while len(remainder) > MAX_CHUNK_CHARS:
            cut = remainder.rfind(". ", 0, MAX_CHUNK_CHARS + 1)
            if cut < MAX_CHUNK_CHARS // 2:
                cut = remainder.rfind(" ", 0, MAX_CHUNK_CHARS + 1)
            if cut < 1:
                cut = MAX_CHUNK_CHARS
            else:
                cut += 1
            result.append(remainder[:cut].strip())
            remainder = remainder[cut:].strip()
        if remainder:
            result.append(remainder)
        return result

    for part_name, part_text in parts:
        paragraphs = [p.strip() for p in re.split(r"\n+", part_text) if p.strip()]
        groups: list[str] = []
        current = ""
        for paragraph in paragraphs:
            if len(paragraph) > MAX_CHUNK_CHARS:
                if current:
                    groups.append(current)
                    current = ""
                groups.extend(split_long_paragraph(paragraph))
                continue
            combined = f"{current}\n{paragraph}" if current else paragraph
            if len(combined) <= MAX_CHUNK_CHARS:
                current = combined
            else:
                if current:
                    groups.append(current)
                current = paragraph
        if current:
            groups.append(current)

        for group in groups:
            if not group.strip():
                continue
            numbered = re.match(r"^(\d{1,3})\.\s+", group)
            section = (
                f"{part_name.title()}-{numbered.group(1)}"
                if numbered else
                f"{part_name.title()}-Preamble"
            )
            first_line = group.splitlines()[0].strip()
            heading = first_line[:120] or f"{part_name.title()} content"
            chunks.append(HTMLChunk(
                chunk_index=len(chunks),
                content=group,
                page_start=None,
                page_end=None,
                section_reference=section,
                heading=heading,
                heading_path=f"{part_name.title()} > {heading}",
                metadata={
                    "content_type": "regulatory_html",
                    "section_reference": section,
                    "document_part": part_name,
                    "page_numbers_available": False,
                },
            ))
    return chunks
