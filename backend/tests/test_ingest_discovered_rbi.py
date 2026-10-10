import os
os.environ.setdefault("DATABASE_URL", "sqlite:///./test-ingest-discovery.db")

from datetime import date

from app.ingestion.discover_rbi import Candidate
from app.ingestion.ingest_discovered_rbi import (
    safe_filename,
    validate_candidate,
)


def candidate(**overrides):
    values = {
        "title": "Maintenance of Cash Reserve Ratio (CRR)",
        "source_url": "https://www.rbi.org.in/Scripts/BS_CircularIndexDisplay.aspx?Id=12858",
        "reference": "RBI/2025-26/46",
        "publication_date": "2025-06-06",
        "department": "Department of Regulation",
        "pdf_url": "https://www.rbi.org.in/commonman/Upload/English/Content/PDF/valid.pdf",
    }
    values.update(overrides)
    return Candidate(**values)


def test_candidate_with_official_pdf_and_metadata_is_eligible():
    ok, reason = validate_candidate(candidate())
    assert ok is True
    assert reason == "eligible"


def test_html_only_candidate_is_skipped_with_explanation():
    ok, reason = validate_candidate(candidate(pdf_url=None))
    assert ok is False
    assert "HTML-only" in reason


def test_non_official_pdf_host_is_rejected():
    ok, reason = validate_candidate(
        candidate(pdf_url="https://example.com/circular.pdf")
    )
    assert ok is False
    assert "approved RBI host" in reason


def test_http_source_is_rejected():
    ok, reason = validate_candidate(
        candidate(source_url="http://www.rbi.org.in/circular")
    )
    assert ok is False
    assert "HTTPS" in reason


def test_placeholder_title_is_rejected():
    ok, reason = validate_candidate(candidate(title="Untitled RBI circular candidate"))
    assert ok is False
    assert "placeholder" in reason


def test_invalid_iso_date_is_rejected():
    ok, reason = validate_candidate(candidate(publication_date="2025-02-30"))
    assert ok is False
    assert "valid ISO date" in reason


def test_reference_is_required_and_validated():
    ok, reason = validate_candidate(candidate(reference=None))
    assert ok is False
    assert "reference" in reason


def test_filename_is_stable_and_filesystem_safe():
    assert safe_filename(candidate()) == "RBI_2025-26_46.pdf"


def test_same_page_fragment_disguised_as_pdf_is_rejected():
    ok, reason = validate_candidate(candidate(
        pdf_url="https://www.rbi.org.in/Scripts/BS_CircularIndexDisplay.aspx?Id=12858#A_1"
    ))
    assert ok is False
    assert "directly to a .pdf" in reason


def test_generic_rbi_website_title_is_rejected():
    ok, reason = validate_candidate(candidate(title="Official Website of Reserve Bank of India"))
    assert ok is False
    assert "placeholder" in reason


def test_html_only_candidate_can_be_validated_when_html_adapter_enabled():
    ok, reason = validate_candidate(candidate(pdf_url=None), allow_html=True)
    assert ok is True
    assert reason == "eligible"


def test_html_candidate_uses_stable_html_filename():
    from app.ingestion.ingest_discovered_rbi import safe_html_filename
    assert safe_html_filename(candidate()) == "RBI_2025-26_46.html"


def test_html_candidate_dry_run_verifies_content_without_database_write(monkeypatch):
    from app.ingestion import ingest_discovered_rbi as ingestion

    sample_chunks = [
        type("Chunk", (), {"content": "Verified circular body"})()
    ]
    monkeypatch.setattr(
        ingestion,
        "_prepare_html_chunks",
        lambda candidate: ("x" * 250, sample_chunks),
    )
    result = ingestion.ingest_candidate(candidate(pdf_url=None), write=False)
    assert result["status"] == "dry_run"
    assert "official HTML content" in result["reason"]
    assert "no database changes made" in result["reason"]
