import os
os.environ.setdefault("DATABASE_URL", "sqlite:///./test-publish-updates.db")

from datetime import date
from types import SimpleNamespace

from app.ingestion.publish_discovered_updates import (
    build_update_payload,
    category_for_document,
)
from app.rag.simplification import (
    RegulatorySimplification,
    RegulatorySimplificationResponse,
    TerminologyItem,
)


def sample_document(**overrides):
    values = {
        "id": 7,
        "title": "Maintenance of Cash Reserve Ratio (CRR)",
        "rbi_reference": "RBI/2025-26/46",
        "source_url": "https://www.rbi.org.in/Scripts/BS_CircularIndexDisplay.aspx?Id=12858",
        "publication_date": date(2025, 6, 6),
        "department": "Department of Regulation",
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def sample_simplification():
    return RegulatorySimplification(
        executive_summary="The circular concerns maintenance of CRR.",
        what_changed="Not explicitly specified in the available RBI material.",
        why_it_matters="Not explicitly specified in the available RBI material.",
        who_is_affected=[],
        what_should_i_do=[
            "No specific implementation action is explicitly specified in the available RBI material."
        ],
        important_dates=[],
        terminology=[TerminologyItem(term="CRR", meaning="Cash Reserve Ratio")],
    )


def sample_result(**overrides):
    values = {
        "evidence_status": "supported",
        "simplification": sample_simplification(),
        "citations": [{
            "chunk_id": 166,
            "document_title": "Maintenance of Cash Reserve Ratio (CRR)",
            "rbi_reference": "RBI/2025-26/46",
            "source_url": "https://www.rbi.org.in/Scripts/BS_CircularIndexDisplay.aspx?Id=12858",
        }],
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_category_classification_uses_known_categories():
    assert category_for_document("Maintenance of Cash Reserve Ratio (CRR)") == "Risk"
    assert category_for_document("Cyber Security Framework for Banks") == "Cyber Security"
    assert category_for_document("Digital Payment Security Controls") == "Digital"
    assert category_for_document("KYC compliance amendment") == "Compliance"
    assert category_for_document("Branch licensing update") == "Banking"


def test_build_update_payload_requires_supported_cited_result():
    payload, reason = build_update_payload(sample_document(), sample_result())

    assert reason == "ready"
    assert payload["document_id"] == 7
    assert payload["title"] == "Maintenance of Cash Reserve Ratio (CRR)"
    assert payload["category"] == "Risk"
    assert payload["publication_date"] == date(2025, 6, 6)
    assert payload["effective_date"] is None
    assert payload["importance"] is None
    assert payload["simplification"]["executive_summary"].startswith(
        "Historical source note — published 6 June 2025."
    )
    assert "The circular concerns maintenance of CRR." in payload["simplification"]["executive_summary"]


def test_build_update_payload_rejects_insufficient_evidence():
    payload, reason = build_update_payload(
        sample_document(),
        sample_result(evidence_status="insufficient", citations=[]),
    )
    assert payload is None
    assert reason == "simplification evidence is insufficient"


def test_build_update_payload_rejects_missing_citations():
    payload, reason = build_update_payload(
        sample_document(),
        sample_result(citations=[]),
    )
    assert payload is None
    assert reason == "simplification has no citations"


def test_build_update_payload_rejects_citation_from_another_document():
    citation = {
        "document_title": "Unrelated circular",
        "rbi_reference": "RBI/2025-26/999",
        "source_url": "https://www.rbi.org.in/unrelated",
    }
    payload, reason = build_update_payload(
        sample_document(),
        sample_result(citations=[citation]),
    )
    assert payload is None
    assert reason == "citation does not match the target document"


def test_build_update_payload_rejects_mismatched_source_url():
    citation = {
        "document_title": "Maintenance of Cash Reserve Ratio (CRR)",
        "rbi_reference": "RBI/2025-26/46",
        "source_url": "https://www.rbi.org.in/another-circular",
    }
    payload, reason = build_update_payload(
        sample_document(),
        sample_result(citations=[citation]),
    )
    assert payload is None
    assert reason == "citation source URL does not match the target document"


def test_historical_note_is_added_only_when_publication_date_is_before_today():
    payload, reason = build_update_payload(
        sample_document(),
        sample_result(),
        today=date(2026, 10, 11),
    )
    assert reason == "ready"
    summary = payload["simplification"]["executive_summary"]
    assert summary.startswith("Historical source note — published 6 June 2025.")
    assert "does not establish whether later RBI directions changed" in summary
    assert "The circular concerns maintenance of CRR." in summary


def test_future_circular_does_not_get_historical_note():
    payload, reason = build_update_payload(
        sample_document(publication_date=date(2027, 1, 1)),
        sample_result(),
        today=date(2026, 10, 11),
    )
    assert reason == "ready"
    assert payload["simplification"]["executive_summary"] == (
        "The circular concerns maintenance of CRR."
    )


def test_missing_publication_date_does_not_get_historical_note():
    payload, reason = build_update_payload(
        sample_document(publication_date=None),
        sample_result(),
        today=date(2026, 10, 11),
    )
    assert reason == "ready"
    assert payload["simplification"]["executive_summary"] == (
        "The circular concerns maintenance of CRR."
    )
