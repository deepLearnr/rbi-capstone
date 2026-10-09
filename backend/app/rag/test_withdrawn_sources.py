from types import SimpleNamespace
from unittest.mock import patch

from app.rag.schemas import RAGAnswer
from app.rag.service import answer_question, parse_evidence_response


def make_result(
    *,
    chunk_id=160,
    status="withdrawn",
    content="The Board is responsible for information security.",
):
    chunk = SimpleNamespace(
        id=chunk_id,
        content=content,
        chunk_metadata={"regulatory_status": status},
    )

    return SimpleNamespace(
        chunk=chunk,
        document_title="Historical UCB Cyber Security Framework",
        rbi_reference="RBI/2019-20/129",
        source_url=None,
        source_file="ucb_cyber_security_framework.pdf",
        page_start=11,
        page_end=11,
        section_reference="Annex IV, Section 6",
        heading="Cyber Security Team/Function",
        distance=0.1,
        regulatory_status=status,
    )


def test_missing_evidence_status_fails_closed():
    status, ids, answer = parse_evidence_response(
        "ANSWER: Some answer without an evidence status"
    )
    assert status == "insufficient"
    assert ids == []


def test_historical_answer_with_withdrawn_citation_gets_warning():
    result = make_result()

    llm_response = (
        "EVIDENCE_STATUS: supported\n"
        "EVIDENCE_IDS: 160\n"
        "ANSWER: The historical framework assigned information-security "
        "responsibility to the Board."
    )

    with (
        patch("app.rag.service.retrieve_chunks", return_value=[result]),
        patch("app.rag.service.get_llm_provider") as get_provider,
        patch("app.rag.service.get_settings") as get_settings,
    ):
        get_settings.return_value.retrieval_top_k = 5
        get_provider.return_value.generate.return_value = llm_response

        answer = answer_question(
            "What did the 2019 framework prescribe for Board governance?",
            top_k=1,
        )

    assert answer.evidence_status == "supported"
    assert len(answer.citations) == 1
    assert answer.citations[0].regulatory_status == "withdrawn"
    assert "withdrawn" in answer.answer.lower()


def test_current_applicability_question_with_only_withdrawn_citation_fails_closed():
    result = make_result()

    llm_response = (
        "EVIDENCE_STATUS: supported\n"
        "EVIDENCE_IDS: 160\n"
        "ANSWER: The Board is responsible for information security."
    )

    with (
        patch("app.rag.service.retrieve_chunks", return_value=[result]),
        patch("app.rag.service.get_llm_provider") as get_provider,
        patch("app.rag.service.get_settings") as get_settings,
    ):
        get_settings.return_value.retrieval_top_k = 5
        get_provider.return_value.generate.return_value = llm_response

        answer = answer_question(
            "What requirements are currently in force?",
            top_k=1,
        )

    assert answer.evidence_status == "insufficient"
    assert answer.citations == []
    assert "does not establish current regulatory applicability" in (
        answer.answer.lower()
    )


def test_invalid_evidence_id_fails_closed():
    result = make_result()

    llm_response = (
        "EVIDENCE_STATUS: supported\n"
        "EVIDENCE_IDS: 999999\n"
        "ANSWER: Unsupported answer."
    )

    with (
        patch("app.rag.service.retrieve_chunks", return_value=[result]),
        patch("app.rag.service.get_llm_provider") as get_provider,
        patch("app.rag.service.get_settings") as get_settings,
    ):
        get_settings.return_value.retrieval_top_k = 5
        get_provider.return_value.generate.return_value = llm_response

        answer = answer_question(
            "What did the historical framework prescribe?",
            top_k=1,
        )

    assert answer.evidence_status == "insufficient"
    assert answer.citations == []
