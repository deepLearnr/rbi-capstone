from types import SimpleNamespace

import pytest

from app.services.learning_scoring import score_assessment


def questions():
    return [
        SimpleNamespace(
            id=1, question="Q1", options=["No", "Yes"], correct_option=1,
            explanation="Yes is correct.", question_order=1,
        ),
        SimpleNamespace(
            id=2, question="Q2", options=["A", "B", "C"], correct_option=0,
            explanation="A is correct.", question_order=2,
        ),
        SimpleNamespace(
            id=3, question="Q3", options=["True", "False"], correct_option=0,
            explanation="True is correct.", question_order=3,
        ),
    ]


def test_all_correct_answers_score_one_hundred_percent():
    result = score_assessment(
        questions(),
        [
            {"question_id": 1, "selected_option": 1},
            {"question_id": 2, "selected_option": 0},
            {"question_id": 3, "selected_option": 0},
        ],
    )
    assert result["correct_count"] == 3
    assert result["total_questions"] == 3
    assert result["score_percent"] == 100
    assert all(answer["is_correct"] for answer in result["answers"])


def test_all_wrong_answers_score_zero_percent():
    result = score_assessment(
        questions(),
        [
            {"question_id": 1, "selected_option": 0},
            {"question_id": 2, "selected_option": 2},
            {"question_id": 3, "selected_option": 1},
        ],
    )
    assert result["correct_count"] == 0
    assert result["score_percent"] == 0
    assert all(not answer["is_correct"] for answer in result["answers"])


def test_answers_are_returned_in_question_order():
    result = score_assessment(
        questions(),
        [
            {"question_id": 3, "selected_option": 0},
            {"question_id": 1, "selected_option": 1},
            {"question_id": 2, "selected_option": 0},
        ],
    )
    assert [answer["question_id"] for answer in result["answers"]] == [1, 2, 3]


def test_selected_option_must_be_integer_or_none():
    with pytest.raises(ValueError):
        score_assessment(
            questions(),
            [
                {"question_id": 1, "selected_option": "1"},
                {"question_id": 2, "selected_option": 0},
                {"question_id": 3, "selected_option": 0},
            ],
        )
