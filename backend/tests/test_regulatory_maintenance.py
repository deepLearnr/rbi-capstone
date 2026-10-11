from copy import deepcopy

import pytest

from app.ingestion.regulatory_maintenance import (
    historicalize_crr_simplification,
    validate_official_rbi_url,
)


def test_official_rbi_url_accepts_https_rbi_domain():
    assert validate_official_rbi_url(
        "https://www.rbi.org.in/Scripts/BS_CircularIndexDisplay.aspx?Id=12858"
    ).startswith("https://www.rbi.org.in/")


@pytest.mark.parametrize(
    "url",
    [
        "http://www.rbi.org.in/example",
        "https://rbi.org.in.attacker.example/example",
        "https://example.com/rbi.org.in",
        "javascript:alert(1)",
        "",
    ],
)
def test_official_rbi_url_rejects_unverified_or_non_official_hosts(url):
    with pytest.raises(ValueError):
        validate_official_rbi_url(url)


def test_crr_historicalization_preserves_note_numbers_and_other_fields():
    original = {
        "executive_summary": (
            "Historical source note — published 6 June 2025. This is a caveat.\n\n"
            "The RBI has decided to reduce the Cash Reserve Ratio (CRR) for all banks "
            "by 100 basis points, bringing it down to 3.0 per cent of net demand and "
            "time Liabilities (NDTL). This reduction will be implemented in four "
            "equal tranches of 25 basis points each."
        ),
        "what_changed": (
            "The average Cash Reserve Ratio (CRR) required to be maintained by every "
            "bank is being reduced in four stages: to 3.75 per cent, 3.5 per cent, "
            "3.25 per cent, and finally to 3.0 per cent of their NDTL."
        ),
        "what_should_i_do": [
            "Banks are required to maintain the CRR at 3.75 per cent, 3.5 per cent, "
            "3.25 per cent and 3.0 per cent of their NDTL effective from the reporting "
            "fortnight beginning September 6, October 4, November 1 and November 29, "
            "2025, respectively."
        ],
        "terminology": [{"term": "CRR", "meaning": "Cash Reserve Ratio"}],
    }
    untouched = deepcopy(original)
    revised, changed = historicalize_crr_simplification(original)

    assert changed is True
    assert revised["executive_summary"].startswith(
        "Historical source note — published 6 June 2025. This is a caveat.\n\n"
    )
    assert "This reduction will be implemented" not in revised["executive_summary"]
    assert "It specified four equal tranches of 25 basis points each." in revised["executive_summary"]
    assert "is being reduced" not in revised["what_changed"]
    assert "Banks are required to maintain" not in revised["what_should_i_do"][0]
    assert "3.75 per cent" in revised["what_should_i_do"][0]
    assert revised["terminology"] == original["terminology"]
    assert original == untouched


def test_crr_historicalization_is_idempotent():
    already_historical = {
        "executive_summary": "The circular stated that the RBI would reduce CRR.",
        "what_changed": "The circular specified a four-stage reduction.",
        "what_should_i_do": ["No explicit action."],
    }
    revised, changed = historicalize_crr_simplification(already_historical)
    assert changed is False
    assert revised == already_historical
