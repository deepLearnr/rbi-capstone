from app.rag.service import parse_evidence_response


def test_parse_supported_response():
    status, evidence_ids, answer = parse_evidence_response(
        """
        EVIDENCE_STATUS: supported
        EVIDENCE_IDS: 91,92,94
        ANSWER: KYC Identifier is a unique number.
        """
    )

    assert status == "supported"
    assert evidence_ids == [91, 92, 94]
    assert answer == "KYC Identifier is a unique number."


def test_parse_insufficient_response():
    status, evidence_ids, answer = parse_evidence_response(
        """
        EVIDENCE_STATUS: insufficient
        EVIDENCE_IDS:
        ANSWER: The available RBI material does not specify this.
        """
    )

    assert status == "insufficient"
    assert evidence_ids == []
    assert answer == (
        "The available RBI material does not specify this."
    )


def test_missing_status_fails_closed():
    status, evidence_ids, answer = parse_evidence_response(
        """
        EVIDENCE_IDS: 91
        ANSWER: Some answer.
        """
    )

    assert status == "insufficient"
    assert evidence_ids == []


def test_invalid_evidence_id_format_fails_closed():
    status, evidence_ids, answer = parse_evidence_response(
        """
        EVIDENCE_STATUS: supported
        EVIDENCE_IDS: Q14
        ANSWER: Some answer.
        """
    )

    assert status == "insufficient"
    assert evidence_ids == []
