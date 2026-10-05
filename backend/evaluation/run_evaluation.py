import json
from pathlib import Path

from app.rag.service import answer_question


ROOT = Path(__file__).resolve().parent
QUESTIONS_FILE = ROOT / "questions.json"


def load_questions() -> list[dict]:
    with QUESTIONS_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def normalize(text: str) -> str:
    return " ".join(text.lower().split())


def evaluate_case(case: dict) -> dict:
    result = answer_question(
        question=case["question"],
        top_k=3,
    )

    sections = {
        citation.section
        for citation in result.citations
        if citation.section
    }

    answer_normalized = normalize(result.answer)

    expected_status_ok = (
        result.evidence_status == case["expected_status"]
    )

    expected_sections = set(case.get("expected_sections", []))
    sections_ok = (
        expected_sections.issubset(sections)
        if expected_sections
        else True
    )

    expected_keywords = case.get("expected_keywords", [])
    if case["language"] == "en" and expected_keywords:
        keywords_ok = all(
            normalize(keyword) in answer_normalized
            for keyword in expected_keywords
        )
    else:
        keywords_ok = bool(answer_normalized)

    # Granular checks breakdown
    checks = {
        "status_match": expected_status_ok,
        "sections_match": sections_ok,
        "keywords_match": keywords_ok,
    }

    passed = all(checks.values())

    return {
        "id": case["id"],
        "language": case["language"],
        "expected_status": case["expected_status"],
        "actual_status": result.evidence_status,
        "expected_sections": sorted(expected_sections),
        "actual_sections": sorted(sections),
        "citations": len(result.citations),
        "checks": checks,
        "passed": passed,
        "answer": result.answer,
    }


def main() -> None:
    cases = load_questions()

    results = []

    print("=" * 72)
    print("RBI Saathi — RAG Evaluation")
    print("=" * 72)

    for case in cases:
        print(f"\n[{case['id']}]")
        print(f"Question: {case['question']}")

        result = evaluate_case(case)
        results.append(result)

        print(f"Expected status: {result['expected_status']}")
        print(f"Actual status:   {result['actual_status']}")
        print(f"Expected sections: {result['expected_sections']}")
        print(f"Actual sections:   {result['actual_sections']}")
        print(f"Citations: {result['citations']}")
        print(f"Checks: {result['checks']}")
        print(f"PASS: {result['passed']}")
        print(f"Answer: {result['answer']}")

    passed = sum(result["passed"] for result in results)
    total = len(results)

    print("\n" + "=" * 72)
    print(f"RESULT: {passed}/{total} cases passed")
    print("=" * 72)

    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()