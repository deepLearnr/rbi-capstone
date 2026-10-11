import os
os.environ.setdefault("DATABASE_URL", "sqlite:///./test-simplification-targeted.db")

import json
from types import SimpleNamespace

from app.rag import simplification


def test_document_scoped_simplification_uses_only_target_document(monkeypatch):
    target = SimpleNamespace(
        chunk=SimpleNamespace(id=166),
        document_title="Maintenance of Cash Reserve Ratio (CRR)",
        rbi_reference="RBI/2025-26/46",
        source_url="https://www.rbi.org.in/Scripts/BS_CircularIndexDisplay.aspx?Id=12858",
        source_file="RBI_2025-26_46.html",
        page_start=None,
        page_end=None,
        heading="Circular-Preamble",
        regulatory_status=None,
    )
    calls = {}

    def retrieve_document_chunks(document_id, top_k):
        calls["document_id"] = document_id
        calls["top_k"] = top_k
        return [target]

    def unexpected_global_retrieval(*args, **kwargs):
        raise AssertionError("document-scoped simplification must not use global retrieval")

    class FakeProvider:
        def generate(self, prompt):
            assert "Maintenance of Cash Reserve Ratio (CRR)" in prompt
            return json.dumps({
                "evidence_status": "supported",
                "evidence_ids": [166],
                "simplification": {
                    "executive_summary": "The circular concerns CRR maintenance.",
                    "what_changed": "Not explicitly specified in the available RBI material.",
                    "why_it_matters": "Not explicitly specified in the available RBI material.",
                    "who_is_affected": [],
                    "what_should_i_do": [
                        "No specific implementation action is explicitly specified in the available RBI material."
                    ],
                    "important_dates": [],
                    "terminology": [],
                },
            })

    monkeypatch.setattr(simplification, "retrieve_document_chunks", retrieve_document_chunks)
    monkeypatch.setattr(simplification, "retrieve_chunks", unexpected_global_retrieval)
    monkeypatch.setattr(simplification, "build_context", lambda results: "target-only evidence")
    monkeypatch.setattr(simplification, "get_llm_provider", lambda: FakeProvider())

    result = simplification.simplify_regulation(
        "Simplify this circular",
        document_id=7,
    )

    assert calls == {"document_id": 7, "top_k": 5}
    assert result.evidence_status == "supported"
    assert result.citations[0]["document_title"] == target.document_title
    assert result.citations[0]["rbi_reference"] == "RBI/2025-26/46"
