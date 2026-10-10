from __future__ import annotations
import argparse
import json
import re
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse, parse_qs
from urllib.request import Request, urlopen

DEFAULT_INDEX_URL = (
    "https://www.rbi.org.in/scripts/bs_circularindexdisplay.aspx/"
    "Scripts/BS_CircularIndexDisplay.aspx"
)
ALLOWED_HOSTS = {"www.rbi.org.in", "rbi.org.in", "m.rbi.org.in"}
USER_AGENT = "RBI-Saathi-CircularDiscovery/1.0"
MAX_HTML_BYTES = 3_000_000
TIMEOUT_SECONDS = 15


@dataclass(frozen=True)
class Candidate:
    title: str
    source_url: str
    reference: str | None = None
    publication_date: str | None = None
    department: str | None = None
    pdf_url: str | None = None
    verification: str = "official_rbi_page_not_yet_ingested"


class _PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.text_parts = []
        self._href = None
        self._anchor_text = []
        self._in_anchor = False
        self._ignored_depth = 0
        self._ignored_tags = {"script", "style", "noscript"}
        self._heading_tag = None
        self._heading_parts = []
        self.headings = []
        self._title_tag = False
        self._title_parts = []
        self.document_title = ""

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        attrs = dict(attrs)
        if tag in self._ignored_tags:
            self._ignored_depth += 1
            return
        if self._ignored_depth:
            return
        if tag in {"h1", "h2"}:
            self._heading_tag = tag
            self._heading_parts = []
        if tag == "title":
            self._title_tag = True
            self._title_parts = []
        if tag == "a" and attrs.get("href"):
            self._href = attrs["href"]
            self._anchor_text = []
            self._in_anchor = True

    def handle_data(self, data):
        if self._ignored_depth:
            return
        clean = " ".join(data.split())
        if data.strip():
            self.text_parts.append(data)
        if self._in_anchor and clean:
            self._anchor_text.append(clean)
        if self._heading_tag and clean:
            self._heading_parts.append(clean)
        if self._title_tag and clean:
            self._title_parts.append(clean)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in self._ignored_tags:
            self._ignored_depth = max(0, self._ignored_depth - 1)
            return
        if self._ignored_depth:
            return
        if tag in {"h1", "h2"} and self._heading_tag:
            heading = " ".join(self._heading_parts).strip()
            if heading:
                self.headings.append(heading)
            self._heading_tag = None
            self._heading_parts = []
        if tag == "title" and self._title_tag:
            self.document_title = " ".join(self._title_parts).strip()
            self._title_tag = False
            self._title_parts = []
        if tag == "a" and self._in_anchor:
            self.links.append((self._href, " ".join(self._anchor_text).strip()))
            self._href = None
            self._anchor_text = []
            self._in_anchor = False


def official_rbi_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return (
            parsed.scheme == "https"
            and parsed.hostname is not None
            and parsed.hostname.lower() in ALLOWED_HOSTS
            and parsed.username is None
            and parsed.password is None
        )
    except ValueError:
        return False


def fetch_html(url: str) -> tuple[str, str]:
    if not official_rbi_url(url):
        raise ValueError(f"Refusing non-official or non-HTTPS URL: {url}")
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html"})
    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            final_url = response.geturl()
            if not official_rbi_url(final_url):
                raise ValueError(f"RBI page redirected outside allowlist: {final_url}")
            content_type = response.headers.get("Content-Type", "").lower()
            if content_type and "html" not in content_type:
                raise ValueError(f"Expected HTML; got {content_type}")
            payload = response.read(MAX_HTML_BYTES + 1)
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError(f"Could not fetch RBI page {url}: {exc}") from exc
    if len(payload) > MAX_HTML_BYTES:
        raise RuntimeError(f"RBI page exceeds {MAX_HTML_BYTES} bytes")
    html = payload.decode("utf-8", errors="replace")
    low = html.lower()
    if ("code in the image" in low or "support id" in low) and "captcha" in low:
        raise RuntimeError("RBI returned a CAPTCHA/challenge page; no records changed.")
    if "enable javascript to view the page content" in low and len(html) < 100_000:
        raise RuntimeError("RBI returned a JavaScript/challenge placeholder.")
    return html, final_url


def _extract_reference(text: str) -> str | None:
    match = re.search(r"\bRBI/\d{4}[-–]\d{2,4}/\d+[A-Z]?\b", text, re.I)
    if match:
        return match.group(0)
    match = re.search(
        r"\b[A-Z]{2,8}(?:\.[A-Z0-9()/-]+){1,8}(?:/\d{4}[-–]\d{2,4})?\b",
        text,
        re.I,
    )
    return match.group(0) if match else None


def _extract_date(text: str) -> str | None:
    patterns = [
        (r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b",
         ("%B %d, %Y", "%B %d %Y")),
        (r"\b\d{1,2}[./-]\d{1,2}[./-]\d{4}\b",
         ("%d.%m.%Y", "%d/%m/%Y", "%d-%m-%Y")),
        (r"\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b",
         ("%d %B %Y",)),
    ]
    for pattern, formats in patterns:
        match = re.search(pattern, text, re.I)
        if not match:
            continue
        raw = match.group(0)
        for fmt in formats:
            try:
                return datetime.strptime(raw, fmt).date().isoformat()
            except ValueError:
                pass
    return None


def parse_index(html: str, page_url: str) -> list[tuple[str, str]]:
    parser = _PageParser()
    parser.feed(html)
    found = {}
    for href, label in parser.links:
        absolute = urljoin(page_url, href)
        if not official_rbi_url(absolute) or not label or len(label) < 5:
            continue
        parsed = urlparse(absolute)
        if "circularindexdisplay.aspx" not in parsed.path.lower():
            continue
        if not any(k.lower() == "id" for k in parse_qs(parsed.query)):
            continue
        found[absolute] = label
    return list(found.items())


def _valid_title(value: str) -> bool:
    title = " ".join((value or "").split()).strip(" -*|")
    low = title.lower()
    if len(title) < 12 or len(title) > 180:
        return False
    blocked_exact = {
        "index to rbi circulars",
        "reserve bank of india",
        "official website of reserve bank of india",
        "untitled rbi circular candidate",
        "home",
        "notifications",
        "all banks",
        "more links",
        "more links :",
        "back to previous page",
        "skip to main content",
    }
    if low in blocked_exact:
        return False
    if (
        "official website of reserve bank of india" in low
        or low.startswith("index to rbi circulars")
        or low.startswith("more links")
    ):
        return False
    blocked_prefixes = (
        "function ", "//redirect", "var ", "window.", "document.",
        "enable javascript", "javascript:", "do you want to",
    )
    if low.startswith(blocked_prefixes):
        return False
    if "function detectmob" in low or "redirect to mobile site" in low:
        return False
    if _extract_reference(title) or _extract_date(title):
        return False
    if re.search(r"\b(?:department of|reserve bank of india)\b", low) and len(title) < 45:
        return False
    return True


def _title_from_content_before_reference(parser: _PageParser, reference: str | None) -> str:
    """Extract RBI's plain-text circular title immediately before its reference.

    Some RBI detail pages render the title as a standalone text node rather than
    an h1/h2. Limit fallback extraction to the circular header region after the
    "Index To RBI Circulars" marker and before the first reference; never search
    arbitrary navigation/footer text for a plausible-looking title.
    """
    if not reference:
        return ""

    ref_index = None
    prefix_in_ref_part = ""
    for index, part in enumerate(parser.text_parts):
        if reference.lower() in part.lower():
            ref_index = index
            prefix_in_ref_part = re.split(re.escape(reference), part, maxsplit=1, flags=re.I)[0]
            break
    if ref_index is None:
        return ""

    prior = parser.text_parts[:ref_index]
    marker_indices = [
        i for i, part in enumerate(prior)
        if "index to rbi circulars" in " ".join(part.split()).lower()
    ]
    if marker_indices:
        candidates = prior[marker_indices[-1] + 1:]
    else:
        candidates = prior[-5:]

    ordered = []
    if prefix_in_ref_part.strip():
        ordered.append(prefix_in_ref_part)
    ordered.extend(reversed(candidates))
    for raw in ordered:
        value = " ".join(raw.split()).strip(" -*|:")
        if not value or re.fullmatch(r"\(?\s*\d+(?:\.\d+)?\s*(?:kb|mb)\s*\)?", value, re.I):
            continue
        if _valid_title(value):
            return value
    return ""


def parse_detail(html: str, source_url: str, link_title: str = "") -> Candidate:
    parser = _PageParser()
    parser.feed(html)
    text = " ".join(" ".join(parser.text_parts).split())
    reference = _extract_reference(text)
    if "index to rbi circulars" not in text.lower() and not reference:
        raise ValueError("Page did not contain recognizable RBI circular metadata.")

    # Only accept direct PDF resources. A label containing "PDF", "download",
    # or "enclosed" is not evidence that the target URL is actually a PDF.
    pdf_url = None
    for href, _label in parser.links:
        absolute = urljoin(source_url, href)
        parsed = urlparse(absolute)
        if (
            official_rbi_url(absolute)
            and parsed.path.lower().endswith(".pdf")
            and parsed.fragment == ""
        ):
            pdf_url = absolute
            break

    # Titles must come from a semantic heading or a credible index-link label.
    # Never guess a title by taking arbitrary body text: RBI pages include
    # scripts, navigation furniture, redirect markers, and generic banners.
    title = ""
    for proposed in [*parser.headings, link_title, parser.document_title]:
        if _valid_title(proposed):
            title = " ".join(proposed.split())
            break
    if not title:
        title = _title_from_content_before_reference(parser, reference)
    if not title:
        title = "Untitled RBI circular candidate"

    low_text = text.lower()
    department = None
    ref_prefix = reference.split("/", 1)[0].upper() if reference else ""
    if ref_prefix == "DOR" or "dor." in low_text or "department of regulation" in low_text:
        department = "Department of Regulation"
    elif "foreign exchange department" in low_text or ref_prefix == "FED":
        department = "Foreign Exchange Department"
    elif "department of supervision" in low_text or ref_prefix == "DOS":
        department = "Department of Supervision"
    elif "financial markets regulation department" in low_text:
        department = "Financial Markets Regulation Department"
    elif "financial inclusion and development department" in low_text:
        department = "Financial Inclusion and Development Department"

    return Candidate(
        title=title,
        source_url=source_url,
        reference=reference,
        publication_date=_extract_date(text),
        department=department,
        pdf_url=pdf_url,
    )


def discover(index_url: str, max_candidates: int = 25, delay: float = 0.25) -> list[Candidate]:
    if max_candidates < 1 or max_candidates > 200:
        raise ValueError("--max-candidates must be between 1 and 200")
    index_html, final_url = fetch_html(index_url)
    # A direct RBI detail URL is also a useful one-record discovery input.
    if any(k.lower() == "id" for k in parse_qs(urlparse(final_url).query)):
        candidate = parse_detail(index_html, final_url)
        return [candidate]
    links = parse_index(index_html, final_url)
    if not links:
        raise RuntimeError(
            "No RBI circular detail links found. The landing page may use a "
            "dynamic month selector or may have returned a challenge page. "
            "Pass a verified official RBI detail/index URL. No database changes made."
        )
    results = []
    seen_refs = set()
    for url, label in links[:max_candidates]:
        try:
            html, final_url = fetch_html(url)
            candidate = parse_detail(html, final_url, label)
            if candidate.reference and candidate.reference in seen_refs:
                continue
            if candidate.reference:
                seen_refs.add(candidate.reference)
            results.append(candidate)
        except (RuntimeError, ValueError) as exc:
            print(f"SKIP {url}: {exc}", file=sys.stderr)
        if delay:
            time.sleep(min(max(delay, 0), 2))
    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Discover candidate circulars from official RBI pages (report-only)."
    )
    parser.add_argument("--index-url", default=DEFAULT_INDEX_URL)
    parser.add_argument("--max-candidates", type=int, default=25)
    parser.add_argument("--output", help="Optional JSON report path.")
    args = parser.parse_args()
    try:
        candidates = discover(args.index_url, args.max_candidates)
    except (RuntimeError, ValueError) as exc:
        print(f"DISCOVERY FAILED: {exc}", file=sys.stderr)
        return 2
    rendered = json.dumps([asdict(x) for x in candidates], ensure_ascii=False, indent=2)
    if args.output:
        from pathlib import Path
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    print(f"Discovered {len(candidates)} candidate(s). Report only; database unchanged.")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
