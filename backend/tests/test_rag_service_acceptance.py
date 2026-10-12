from types import SimpleNamespace

import pytest

from app.rag import service


def retrieved(chunk_id=10, status="active"):
    return SimpleNamespace(
        chunk=SimpleNamespace(id=chunk_id, content="The circular describes the applicable regulatory requirement."),
        document_title="Test RBI circular",
        rbi_reference="RBI/TEST/1",
        source_file="test.pdf",
        source_url="https://www.rbi.org.in/test",
        page_start=1,
        page_end=2,
        heading="Test section",
        regulatory_status=status,
        distance=0.1,
    )


class FakeProvider:
    def __init__(self, response):
        self.response = response
        self.calls = 0

    def generate(self, prompt):
        self.calls += 1
        return self.response


def patch_rag(monkeypatch, results, response=None):
    provider = FakeProvider(response or "")
    monkeypatch.setattr(service, "retrieve_chunks", lambda *a, **kw: results)
    monkeypatch.setattr(
        service, "get_settings",
        lambda: SimpleNamespace(retrieval_top_k=3),
    )
    monkeypatch.setattr(service, "get_llm_provider", lambda: provider)
    return provider


def test_empty_retrieval_fails_closed_without_calling_llm(monkeypatch):
    provider = patch_rag(monkeypatch, [], "EVIDENCE_STATUS: supported\nEVIDENCE_IDS: 10\nANSWER: invented")
    result = service.answer_question("What is the current rule?")
    assert result.evidence_status == "insufficient"
    assert result.citations == []
    assert "not contain enough information" in result.answer
    assert provider.calls == 0


def test_model_cannot_cite_chunk_not_retrieved(monkeypatch):
    provider = patch_rag(
        monkeypatch,
        [retrieved(10)],
        "EVIDENCE_STATUS: supported\nEVIDENCE_IDS: 999\nANSWER: Unsupported claim",
    )
    result = service.answer_question("What does this circular say?")
    assert result.evidence_status == "insufficient"
    assert result.citations == []
    assert "not contain enough information" in result.answer
    assert provider.calls == 1


def test_withdrawn_only_evidence_cannot_answer_current_applicability(monkeypatch):
    patch_rag(
        monkeypatch,
        [retrieved(10, "withdrawn")],
        "EVIDENCE_STATUS: supported\nEVIDENCE_IDS: 10\nANSWER: The rule is currently applicable.",
    )
    result = service.answer_question("Is this rule currently applicable?")
    assert result.evidence_status == "insufficient"
    assert result.citations == []
    assert "withdrawn" in result.answer.lower()
    assert "current regulatory applicability" in result.answer.lower()


def test_unknown_source_status_cannot_establish_current_applicability(
    monkeypatch,
):
    patch_rag(
        monkeypatch,
        [retrieved(10, status=None)],
        (
            "EVIDENCE_STATUS: supported\n"
            "EVIDENCE_IDS: 10\n"
            "ANSWER: The current CRR requirement is 3.0 percent."
        ),
    )

    result = service.answer_question(
        "What is the current CRR requirement in force today?"
    )

    assert result.evidence_status == "insufficient"
    assert result.citations == []
    assert "does not establish current regulatory applicability" in (
        result.answer.lower()
    )


def test_historical_answer_with_withdrawn_source_gets_warning(monkeypatch):
    patch_rag(
        monkeypatch,
        [retrieved(10, "withdrawn")],
        "EVIDENCE_STATUS: supported\nEVIDENCE_IDS: 10\nANSWER: The circular stated the earlier requirement.",
    )
    result = service.answer_question("What did the old circular state?")
    assert result.evidence_status == "supported"
    assert len(result.citations) == 1
    assert "historical-source warning" in result.answer.lower()


def test_question_whitespace_is_trimmed_before_retrieval(monkeypatch):
    seen = {}
    provider = patch_rag(
        monkeypatch,
        [retrieved(10)],
        "EVIDENCE_STATUS: supported\nEVIDENCE_IDS: 10\nANSWER: Supported answer.",
    )
    original = service.retrieve_chunks

    def capture(question, **kwargs):
        seen["question"] = question
        return original(question, **kwargs)

    monkeypatch.setattr(service, "retrieve_chunks", capture)
    result = service.answer_question("  What does the circular say?  ")
    assert seen["question"] == "What does the circular say?"
    assert result.evidence_status == "supported"
    assert len(result.citations) == 1
