from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models.assessment import Assessment
from app.models.assessment_attempt import AssessmentAttempt
from app.models.learning_module import LearningModule
from app.models.learning_progress import LearningProgress
from app.schemas.learning import AssessmentSubmitRequest, ProgressUpdateRequest
from app.services.learning_scoring import score_assessment

router = APIRouter(prefix="/api/learning", tags=["Learning and Assessments"])


def _module_summary(module, progress=None):
    return {
        "id": module.id,
        "title": module.title,
        "category": module.category,
        "description": module.description,
        "difficulty": module.difficulty,
        "estimated_minutes": module.estimated_minutes,
        "status": module.status,
        "document_id": module.document_id,
        "regulatory_update_id": module.regulatory_update_id,
        "progress_percent": progress.progress_percent if progress else 0,
        "completed": progress.completed if progress else False,
        "section_count": len(module.sections),
        "assessment_count": len(module.assessments),
    }


def _assessment_summary(assessment):
    return {
        "id": assessment.id,
        "module_id": assessment.module_id,
        "module_title": assessment.module.title,
        "title": assessment.title,
        "description": assessment.description,
        "question_count": len(assessment.questions),
        "duration_minutes": assessment.duration_minutes or 10,
        "passing_score": assessment.passing_score,
    }


def _attempt_out(attempt):
    assessment = attempt.assessment
    answers = attempt.answers or []
    return {
        "id": attempt.id,
        "assessment_id": attempt.assessment_id,
        "assessment_title": assessment.title,
        "module_id": assessment.module_id,
        "module_title": assessment.module.title,
        "score_percent": attempt.score,
        "correct_count": sum(1 for answer in answers if answer.get("is_correct")),
        "total_questions": attempt.total_questions,
        "passed": attempt.passed,
        "answers": answers,
        "completed_at": attempt.completed_at.isoformat(),
    }


@router.get("/modules")
def list_modules(db: Session = Depends(get_db)):
    modules = (
        db.query(LearningModule)
        .options(
            joinedload(LearningModule.sections),
            joinedload(LearningModule.assessments),
        )
        .filter(LearningModule.status == "published")
        .order_by(LearningModule.id)
        .all()
    )
    progress_by_module = {
        row.module_id: row
        for row in db.query(LearningProgress).all()
    }
    return [
        _module_summary(module, progress_by_module.get(module.id))
        for module in modules
    ]


@router.get("/modules/{module_id}")
def get_module(module_id: int, db: Session = Depends(get_db)):
    module = (
        db.query(LearningModule)
        .options(
            joinedload(LearningModule.sections),
            joinedload(LearningModule.assessments).joinedload(Assessment.questions),
        )
        .filter(
            LearningModule.id == module_id,
            LearningModule.status == "published",
        )
        .first()
    )
    if module is None:
        raise HTTPException(status_code=404, detail="Learning module not found.")

    progress = (
        db.query(LearningProgress)
        .filter(LearningProgress.module_id == module.id)
        .one_or_none()
    )
    data = _module_summary(module, progress)
    data["sections"] = [
        {
            "id": section.id,
            "title": section.title,
            "content": section.content,
            "section_order": section.section_order,
        }
        for section in module.sections
    ]
    data["assessments"] = [
        _assessment_summary(assessment)
        for assessment in module.assessments
    ]
    return data


@router.post("/modules/{module_id}/progress")
def update_module_progress(
    module_id: int,
    payload: ProgressUpdateRequest,
    db: Session = Depends(get_db),
):
    module = db.get(LearningModule, module_id)
    if module is None or module.status != "published":
        raise HTTPException(status_code=404, detail="Learning module not found.")

    # Demo scope: progress is shared by the single demo learner because the
    # project does not yet have authenticated user identities.
    progress = (
        db.query(LearningProgress)
        .filter(LearningProgress.module_id == module_id)
        .one_or_none()
    )
    if progress is None:
        progress = LearningProgress(module_id=module_id)
        db.add(progress)

    progress.progress_percent = payload.progress_percent
    progress.completed = payload.progress_percent == 100
    progress.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(progress)
    return {
        "module_id": progress.module_id,
        "progress_percent": progress.progress_percent,
        "completed": progress.completed,
        "updated_at": progress.updated_at.isoformat(),
    }


@router.get("/assessments")
def list_assessments(db: Session = Depends(get_db)):
    assessments = (
        db.query(Assessment)
        .join(LearningModule)
        .options(
            joinedload(Assessment.module),
            joinedload(Assessment.questions),
        )
        .filter(LearningModule.status == "published")
        .order_by(Assessment.id)
        .all()
    )
    return [_assessment_summary(item) for item in assessments]


@router.get("/assessments/{assessment_id}")
def get_assessment(assessment_id: int, db: Session = Depends(get_db)):
    assessment = (
        db.query(Assessment)
        .options(
            joinedload(Assessment.module),
            joinedload(Assessment.questions),
        )
        .filter(Assessment.id == assessment_id)
        .first()
    )
    if assessment is None or assessment.module.status != "published":
        raise HTTPException(status_code=404, detail="Assessment not found.")

    # Deliberately do not expose correct_option or explanation before submission.
    return {
        **_assessment_summary(assessment),
        "questions": [
            {
                "id": question.id,
                "question": question.question,
                "options": question.options,
                "question_order": question.question_order,
            }
            for question in assessment.questions
        ],
    }


@router.post("/assessments/{assessment_id}/attempts")
def submit_assessment(
    assessment_id: int,
    payload: AssessmentSubmitRequest,
    db: Session = Depends(get_db),
):
    assessment = (
        db.query(Assessment)
        .options(
            joinedload(Assessment.module),
            joinedload(Assessment.questions),
        )
        .filter(Assessment.id == assessment_id)
        .first()
    )
    if assessment is None or assessment.module.status != "published":
        raise HTTPException(status_code=404, detail="Assessment not found.")

    try:
        result = score_assessment(assessment.questions, payload.answers)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    passed = result["score_percent"] >= assessment.passing_score
    attempt = AssessmentAttempt(
        assessment_id=assessment.id,
        score=result["score_percent"],
        total_questions=result["total_questions"],
        passed=passed,
        answers=result["answers"],
        completed_at=datetime.utcnow(),
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return {
        **_attempt_out(attempt),
        "passing_score": assessment.passing_score,
    }


@router.get("/attempts")
def list_attempts(db: Session = Depends(get_db)):
    attempts = (
        db.query(AssessmentAttempt)
        .options(
            joinedload(AssessmentAttempt.assessment).joinedload(Assessment.module)
        )
        .order_by(AssessmentAttempt.completed_at.desc(), AssessmentAttempt.id.desc())
        .all()
    )
    return [_attempt_out(attempt) for attempt in attempts]


@router.get("/progress")
def get_progress(db: Session = Depends(get_db)):
    modules = (
        db.query(LearningModule)
        .filter(LearningModule.status == "published")
        .order_by(LearningModule.id)
        .all()
    )
    progress_rows = {p.module_id: p for p in db.query(LearningProgress).all()}
    module_items = [
        {
            "module_id": module.id,
            "title": module.title,
            "category": module.category,
            "progress_percent": progress_rows[module.id].progress_percent
                if module.id in progress_rows else 0,
            "completed": progress_rows[module.id].completed
                if module.id in progress_rows else False,
        }
        for module in modules
    ]
    attempts = (
        db.query(AssessmentAttempt)
        .order_by(AssessmentAttempt.completed_at.desc())
        .all()
    )
    overall = round(
        sum(item["progress_percent"] for item in module_items) / len(module_items)
    ) if module_items else 0
    average_score = round(
        sum(attempt.score for attempt in attempts) / len(attempts)
    ) if attempts else 0
    return {
        "modules": module_items,
        "overall_progress": overall,
        "modules_completed": sum(1 for item in module_items if item["completed"]),
        "module_count": len(module_items),
        "assessment_average": average_score,
        "attempts_count": len(attempts),
    }
