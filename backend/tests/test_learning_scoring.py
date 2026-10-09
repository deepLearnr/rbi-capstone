from types import SimpleNamespace

import pytest

from app.services.learning_scoring import score_assessment


@pytest.fixture
def questions():
    return [
        SimpleNamespace(
            id=10,
            question="First?",
            options=["A", "B"],
            correct_option=1,
            explanation="B is correct.",
            question_order=1,
        ),
        SimpleNamespace(
            id=11,
            question="Second?",
            options=["A", "B", "C"],
            correct_option=0,
            explanation="A is correct.",
            question_order=2,
        ),
    ]


def test_score_assessment_calculates_percentage_and_review(questions):
    result = score_assessment(
        questions,
        [
            {"question_id": 10, "selected_option": 1},
            {"question_id": 11, "selected_option": 2},
        ],
    )
    assert result["correct_count"] == 1
    assert result["total_questions"] == 2
    assert result["score_percent"] == 50
    assert result["answers"][0]["is_correct"] is True
    assert result["answers"][1]["correct_option"] == 0


def test_score_assessment_allows_unanswered_question(questions):
    result = score_assessment(
        questions,
        [
            {"question_id": 10, "selected_option": None},
            {"question_id": 11, "selected_option": 0},
        ],
    )
    assert result["correct_count"] == 1
    assert result["score_percent"] == 50


@pytest.mark.parametrize(
    "answers",
    [
        [{"question_id": 10, "selected_option": 1}],
        [
            {"question_id": 10, "selected_option": 1},
            {"question_id": 10, "selected_option": 0},
        ],
        [
            {"question_id": 10, "selected_option": 1},
            {"question_id": 999, "selected_option": 0},
        ],
        [
            {"question_id": 10, "selected_option": 9},
            {"question_id": 11, "selected_option": 0},
        ],
    ],
)
def test_score_assessment_rejects_invalid_payloads(questions, answers):
    with pytest.raises(ValueError):
        score_assessment(questions, answers)
