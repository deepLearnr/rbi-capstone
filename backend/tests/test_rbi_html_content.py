from app.ingestion.discover_rbi import Candidate
from app.ingestion.rbi_html_content import (
    chunk_html_content,
    extract_circular_html_content,
)


def _candidate():
    return Candidate(
        title="Maintenance of Cash Reserve Ratio (CRR)",
        source_url="https://www.rbi.org.in/Scripts/BS_CircularIndexDisplay.aspx?Id=12858",
        reference="RBI/2025-26/46",
        publication_date="2025-06-06",
        department="Department of Regulation",
        pdf_url=None,
    )


def test_extracts_circular_body_and_excludes_scripts_and_archive():
    html = """
    <html><head><script>function detectmob() { bad(); }</script></head>
    <body>
      <nav>Home Notifications</nav>
      <h1>Index To RBI Circulars</h1>
      <main>
        <h2>Maintenance of Cash Reserve Ratio (CRR)</h2>
        <p>RBI/2025-26/46</p>
        <p>DoR.RET.REC.23/12.01.001/2025-26 June 06, 2025</p>
        <p>All banks, Madam / Sir, Maintenance of Cash Reserve Ratio (CRR)</p>
        <p>Please refer to the previous circular on the captioned subject.</p>
        <p>Accordingly, banks are required to maintain the CRR at 3.75 per cent,
        3.5 per cent, 3.25 per cent and 3.0 per cent of NDTL over four fortnights.</p>
        <p>This instruction is issued under the relevant statutory authority.</p>
      </main>
      <h2>Archives</h2><p>2016 January February</p>
      <footer>More Links Follow RBI</footer>
    </body></html>
    """
    content = extract_circular_html_content(html, _candidate())
    assert content.startswith("Maintenance of Cash Reserve Ratio (CRR)")
    assert "RBI/2025-26/46" in content
    assert "detectmob" not in content
    assert "2016 January February" not in content
    assert len(content) >= 200


def test_html_content_rejects_shell_without_substantial_body():
    html = """
    <html><body><h1>Maintenance of Cash Reserve Ratio (CRR)</h1>
    <p>RBI/2025-26/46</p><p>Archives</p></body></html>
    """
    try:
        extract_circular_html_content(html, _candidate())
    except ValueError as exc:
        assert "too short" in str(exc)
    else:
        raise AssertionError("short redirect/page shell should be rejected")


def test_html_chunker_preserves_content_without_fabricating_pages():
    content = (
        "Maintenance of Cash Reserve Ratio (CRR)\n"
        "RBI/2025-26/46\n"
        + ("Banks shall maintain the required reserve ratio. " * 100)
    )
    chunks = chunk_html_content(content)
    assert len(chunks) >= 2
    assert "".join(chunk.content for chunk in chunks).replace("\n", " ").replace("  ", " ")
    assert all(chunk.page_start is None and chunk.page_end is None for chunk in chunks)
    assert all(chunk.metadata["content_type"] == "regulatory_html" for chunk in chunks)
    assert all(len(chunk.content) <= 1800 for chunk in chunks)



def test_extract_trims_rbi_archive_calendar_without_explicit_footer_marker():
    body = (
        "Maintenance of Cash Reserve Ratio (CRR)\n"
        "RBI/2025-26/46\n"
        "DoR.RET.REC.23/12.01.001/2025-26\n"
        "June 06, 2025\n"
        "All banks, Madam / Sir, Maintenance of Cash Reserve Ratio (CRR)\n"
        "The Reserve Bank has decided to reduce the Cash Reserve Ratio.\n"
        "Banks are required to maintain CRR in four equal tranches as notified.\n"
        "NOTIFICATION\n"
        "In exercise of the powers conferred under the RBI Act, the Reserve Bank notifies the revised ratio.\n"
        "(Executive Director)\n"
        "2026\nAll Months\nJanuary\nFebruary\nMarch\nApril\nMay\n"
        "2025\nAll Months\nJanuary\nFebruary\nMarch\nApril\nMay\n"
    )
    html = "<html><body>" + "".join(
        f"<p>{line}</p>" for line in body.splitlines()
    ) + "</body></html>"
    content = extract_circular_html_content(html, _candidate())
    assert "NOTIFICATION" in content
    assert "Executive Director" in content
    assert "2026\nAll Months" not in content
    assert "January" not in content
    assert "February" not in content


def test_archive_calendar_detection_does_not_trim_year_without_month_widget():
    from app.ingestion.rbi_html_content import _trim_archive_calendar

    text = "Circular issued in 2026\nAll Months\nThis applies to banks."
    assert _trim_archive_calendar(text) == text


def test_chunker_keeps_attached_notification_separate_from_main_circular():
    content = (
        "Maintenance of Cash Reserve Ratio (CRR)\n"
        "RBI/2025-26/46\n"
        "2. Banks shall maintain the CRR at the notified levels.\n"
        "Yours faithfully,\n(Officer)\nEncl.: As above\n"
        "DoR.RET.REC.24/12.01.001/2025-26\n"
        "June 06, 2025\n"
        "NOTIFICATION\n"
        "In exercise of statutory powers, the Reserve Bank hereby notifies "
        "the required CRR levels for all banks."
    )
    chunks = chunk_html_content(content)
    circular = [c for c in chunks if c.metadata["document_part"] == "circular"]
    notification = [c for c in chunks if c.metadata["document_part"] == "notification"]

    assert circular and notification
    assert all("NOTIFICATION" not in c.content for c in circular)
    assert notification[0].content.startswith("NOTIFICATION")
    assert notification[0].heading_path.startswith("Notification >")
    assert "In exercise of statutory powers" in "\n".join(c.content for c in chunks)
