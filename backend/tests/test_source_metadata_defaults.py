from datetime import date
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.ingestion import ingest_kyc_faq, ingest_regulatory, ingest_document
from app.ingestion.profiles import DOCUMENT_PROFILES


def test_kyc_faq_metadata_has_verified_source_and_date():
    metadata = ingest_kyc_faq.build_faq_document_data("RBI_KYC.pdf")

    assert metadata["source_file"] == "RBI_KYC.pdf"
    assert metadata["publication_date"] == date(2025, 6, 9)
    assert metadata["source_url"] == (
        "https://www.rbi.org.in/commonperson/english/Scripts/FAQs.aspx?Id=3782"
    )
    assert "regulatory_status" not in metadata


def test_kyc_amendment_ingestion_defaults_to_verified_official_url(monkeypatch):
    monkeypatch.setattr(
        ingest_regulatory,
        "extract_pdf_pages",
        lambda _path: [SimpleNamespace(page_number=1, text="source text")],
    )
    monkeypatch.setattr(
        ingest_regulatory,
        "chunk_regulatory_pages",
        lambda _pages: [SimpleNamespace(chunk_index=0, content="source text")],
    )

    metadata, chunks = ingest_regulatory.build_regulatory_document(
        "KYC_Rule_Commercial.pdf"
    )

    assert metadata["rbi_reference"] == "RBI/2026-27/257"
    assert metadata["publication_date"] == date(2026, 9, 18)
    assert metadata["source_url"] == (
        "https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=13699&Mode=0"
    )
    assert len(chunks) == 1


def test_kyc_amendment_ingestion_rejects_non_official_url_override():
    with pytest.raises(ValueError, match="official rbi.org.in domain"):
        ingest_regulatory.build_regulatory_document(
            "KYC_Rule_Commercial.pdf",
            source_url="https://rbi.org.in.attacker.example/notification",
        )


def test_ucb_cyber_profile_preserves_verified_url_and_withdrawn_status():
    profile = DOCUMENT_PROFILES["ucb_cyber_security_framework.pdf"]

    assert profile.source_url == (
        "https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=11772"
    )
    assert profile.regulatory_status == "withdrawn"


def test_profiled_ingestion_passes_profile_source_url_to_persistence(
    monkeypatch, tmp_path: Path
):
    profile = DOCUMENT_PROFILES["ucb_cyber_security_framework.pdf"]
    pdf_path = tmp_path / profile.source_file
    pdf_path.write_bytes(b"test fixture; extraction is stubbed")
    observed = {}

    monkeypatch.setattr(
        ingest_document,
        "extract_pdf_pages",
        lambda _path: [SimpleNamespace(page_number=1, text="source text")],
    )
    monkeypatch.setitem(
        ingest_document.CHUNKERS,
        "ucb_cyber",
        lambda _pages: [SimpleNamespace(chunk_index=0, content="source text")],
    )

    def capture_persist_document(*args, **kwargs):
        observed.update(kwargs)
        return SimpleNamespace(document_id=1, chunk_count=1, dry_run=True)

    monkeypatch.setattr(ingest_document, "persist_document", capture_persist_document)

    ingest_document.ingest_profiled_pdf(pdf_path, dry_run=True)

    assert observed["source_url"] == profile.source_url
