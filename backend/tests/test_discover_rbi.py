from app.ingestion.discover_rbi import official_rbi_url, parse_detail, parse_index


def test_official_url_allowlist_requires_https_and_exact_host():
    assert official_rbi_url("https://www.rbi.org.in/Scripts/BS_CircularIndexDisplay.aspx?Id=1")
    assert official_rbi_url("https://m.rbi.org.in/path")
    assert not official_rbi_url("http://www.rbi.org.in/path")
    assert not official_rbi_url("https://rbi.org.in.attacker.example/path")
    assert not official_rbi_url("https://example.com/path")


def test_parse_index_only_keeps_official_circular_detail_links():
    html = '''
    <html><body>
      <a href="/Scripts/BS_CircularIndexDisplay.aspx?Id=123">Cash Reserve Ratio circular</a>
      <a href="https://example.com/Scripts/BS_CircularIndexDisplay.aspx?Id=8">Fake link</a>
      <a href="/about">About RBI</a>
    </body></html>
    '''
    links = parse_index(html, "https://www.rbi.org.in/index")
    assert links == [
        ("https://www.rbi.org.in/Scripts/BS_CircularIndexDisplay.aspx?Id=123",
         "Cash Reserve Ratio circular")
    ]


def test_parse_detail_extracts_reference_and_official_pdf():
    html = '''
    <html><body>
      <h1>Amendment to Master Direction - KYC</h1>
      RBI/2024-25/87 Department of Regulation November 6, 2024
      <a href="/Scripts/BS_CircularIndexDisplay.aspx?Id=12">Index To RBI Circulars</a>
      <a href="/upload/kyc.pdf">Download PDF</a>
    </body></html>
    '''
    result = parse_detail(
        html, "https://www.rbi.org.in/Scripts/BS_CircularIndexDisplay.aspx?Id=12",
        "Amendment to Master Direction - KYC",
    )
    assert result.reference == "RBI/2024-25/87"
    assert result.publication_date == "2024-11-06"
    assert result.department == "Department of Regulation"
    assert result.pdf_url == "https://www.rbi.org.in/upload/kyc.pdf"



def test_parse_detail_uses_circular_title_from_page_body_when_direct_url():
    html = """
    <html><body>
      <h1>Maintenance of Cash Reserve Ratio (CRR)</h1>
      Index To RBI Circulars
      RBI/2025-26/46
      DoR.RET.REC.23/12.01.001/2025-26 June 06, 2025
      All banks
    </body></html>
    """
    result = parse_detail(
        html,
        "https://www.rbi.org.in/Scripts/BS_CircularIndexDisplay.aspx?Id=12858",
    )
    assert result.title == "Maintenance of Cash Reserve Ratio (CRR)"
    assert result.reference == "RBI/2025-26/46"
    assert result.publication_date == "2025-06-06"
    assert result.department == "Department of Regulation"


def test_parse_detail_ignores_same_page_fragment_labeled_pdf():
    html = """
    <html><head><title>Official Website of Reserve Bank of India</title></head>
    <body>
      <h1>Maintenance of Cash Reserve Ratio (CRR)</h1>
      RBI/2025-26/46
      DoR.RET.REC.23/12.01.001/2025-26 June 06, 2025
      <a href="/Scripts/BS_CircularIndexDisplay.aspx?Id=12858#A_1">PDF</a>
    </body></html>
    """
    result = parse_detail(
        html, "https://www.rbi.org.in/Scripts/BS_CircularIndexDisplay.aspx?Id=12858"
    )
    assert result.title == "Maintenance of Cash Reserve Ratio (CRR)"
    assert result.pdf_url is None



def test_parse_detail_does_not_treat_mobile_redirect_marker_as_title_or_pdf():
    html = """
    <html><head><title>Official Website of Reserve Bank of India</title></head>
    <body>
      //Redirect to mobile site start
      RBI/2025-26/46
      June 06, 2025
      <a href="/Scripts/BS_CircularIndexDisplay.aspx?Id=12858#A_1">PDF</a>
    </body></html>
    """
    result = parse_detail(
        html, "https://www.rbi.org.in/Scripts/BS_CircularIndexDisplay.aspx?Id=12858",
        "Official Website of Reserve Bank of India",
    )
    assert result.title == "Untitled RBI circular candidate"
    assert result.pdf_url is None


def test_parse_detail_requires_direct_pdf_path_not_download_label():
    html = """
    <html><body>
      <h1>Maintenance of Cash Reserve Ratio (CRR)</h1>
      RBI/2025-26/46 June 06, 2025
      <a href="/Scripts/BS_CircularIndexDisplay.aspx?Id=12858">Download PDF</a>
    </body></html>
    """
    result = parse_detail(
        html, "https://www.rbi.org.in/Scripts/BS_CircularIndexDisplay.aspx?Id=12858"
    )
    assert result.pdf_url is None



def test_parse_detail_ignores_javascript_and_redirect_text_as_title():
    html = """
    <html><head><title>Official Website of Reserve Bank of India</title>
    <script>function detectmob() { return true; }</script></head>
    <body>
      //Redirect to mobile site start
      RBI/2025-26/46
      June 06, 2025
      <a href="/Scripts/BS_CircularIndexDisplay.aspx?Id=12858#A_1">Download PDF</a>
    </body></html>
    """
    result = parse_detail(
        html,
        "https://www.rbi.org.in/Scripts/BS_CircularIndexDisplay.aspx?Id=12858",
    )
    assert result.title == "Untitled RBI circular candidate"
    assert result.pdf_url is None


def test_parse_detail_ignores_generic_site_heading_and_requires_real_title():
    html = """
    <html><body>
      <h1>Official Website of Reserve Bank of India</h1>
      RBI/2025-26/46 June 06, 2025
    </body></html>
    """
    result = parse_detail(
        html,
        "https://www.rbi.org.in/Scripts/BS_CircularIndexDisplay.aspx?Id=12858",
    )
    assert result.title == "Untitled RBI circular candidate"


def test_parse_detail_extracts_plain_text_title_before_reference():
    # RBI's live layout places the circular title in a plain text node after
    # the generic "Index To RBI Circulars" heading and file-size label.
    html = """
    <html><head><title>Index To RBI Circulars | Official Website of Reserve Bank of India</title></head>
    <body>
      <h1>Index To RBI Circulars</h1>
      <div>(283 kb)</div>
      <div>Maintenance of Cash Reserve Ratio (CRR)</div>
      <div>RBI/2025-26/46</div>
      <div>DoR.RET.REC.23/12.01.001/2025-26 June 06, 2025 All banks</div>
      <div>More Links :</div>
    </body></html>
    """
    result = parse_detail(
        html, "https://www.rbi.org.in/Scripts/BS_CircularIndexDisplay.aspx?Id=12858"
    )
    assert result.title == "Maintenance of Cash Reserve Ratio (CRR)"
    assert result.reference == "RBI/2025-26/46"
    assert result.publication_date == "2025-06-06"
    assert result.pdf_url is None


def test_parse_detail_does_not_use_more_links_as_title_when_content_missing():
    html = """
    <html><body>
      <h1>Index To RBI Circulars</h1>
      <div>(283 kb)</div>
      <div>RBI/2025-26/46</div>
      <div>More Links :</div>
    </body></html>
    """
    result = parse_detail(
        html, "https://www.rbi.org.in/Scripts/BS_CircularIndexDisplay.aspx?Id=12858"
    )
    assert result.title == "Untitled RBI circular candidate"
