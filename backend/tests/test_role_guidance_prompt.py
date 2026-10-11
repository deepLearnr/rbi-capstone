from app.rag.prompt import ROLE_GUIDANCE, build_rag_prompt


def test_role_guidance_covers_expected_roles():
    assert set(ROLE_GUIDANCE) == {
        "bank_employee",
        "compliance_officer",
        "branch_manager",
        "customer_support",
    }


def test_role_guidance_never_overrides_evidence_requirements():
    for role, guidance in ROLE_GUIDANCE.items():
        assert guidance.strip()
        assert "source" in guidance.lower() or role == "branch_manager"


def test_prompt_applies_role_framing_without_replacing_evidence_rules(monkeypatch):
    monkeypatch.setattr("app.rag.prompt.build_context", lambda results: "EVIDENCE_ID: 12\nSupported source text.")
    prompt = build_rag_prompt(
        question="What should I do?",
        results=[],
        role="compliance_officer",
    )
    assert "compliance officer" in prompt
    assert "ROLE-SPECIFIC PRESENTATION GUIDANCE" in prompt
    assert "does not change the source evidence standard" in prompt
    assert "EVIDENCE_STATUS: supported" in prompt
