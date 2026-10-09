def score_assessment(questions, submitted_answers):
    """Validate a complete answer payload and calculate results server-side.

    Questions may be SQLAlchemy AssessmentQuestion instances. Submitted answers
    may be Pydantic objects or dictionaries. The caller should persist the
    returned review payload only after this function succeeds.
    """
    if not questions:
        raise ValueError("This assessment has no questions.")

    def value(item, key):
        return item.get(key) if isinstance(item, dict) else getattr(item, key)

    question_by_id = {question.id: question for question in questions}
    if len(question_by_id) != len(questions):
        raise ValueError("Assessment contains duplicate question IDs.")

    answers_by_id = {}
    for answer in submitted_answers:
        question_id = value(answer, "question_id")
        if question_id not in question_by_id:
            raise ValueError(f"Unknown question ID: {question_id}.")
        if question_id in answers_by_id:
            raise ValueError(f"Duplicate answer for question ID: {question_id}.")
        answers_by_id[question_id] = value(answer, "selected_option")

    if set(answers_by_id) != set(question_by_id):
        raise ValueError("Submit one answer entry for every assessment question.")

    review = []
    correct_count = 0

    for question in questions:
        selected = answers_by_id[question.id]
        options = question.options or []
        correct = question.correct_option

        if not isinstance(correct, int) or correct < 0 or correct >= len(options):
            raise ValueError(f"Question {question.id} has an invalid answer key.")
        if selected is not None:
            if isinstance(selected, bool) or not isinstance(selected, int):
                raise ValueError(f"Selected option for question {question.id} must be an integer or null.")
            if selected < 0 or selected >= len(options):
                raise ValueError(f"Selected option for question {question.id} is out of range.")

        is_correct = selected is not None and selected == correct
        correct_count += int(is_correct)
        review.append({
            "question_id": question.id,
            "question": question.question,
            "options": options,
            "selected_option": selected,
            "correct_option": correct,
            "is_correct": is_correct,
            "explanation": question.explanation,
        })

    total = len(questions)
    percentage = round(correct_count * 100 / total)
    return {
        "correct_count": correct_count,
        "total_questions": total,
        "score_percent": percentage,
        "answers": review,
    }
