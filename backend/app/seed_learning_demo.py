"""Idempotently seed a small, general KYC learning demo.

The content is foundational training, not a statement of current legal
requirements. Follow applicable current RBI directions and the institution's
approved policies for real compliance decisions.
"""
from app.db.session import SessionLocal
from app.models import (
    Assessment,
    AssessmentQuestion,
    LearningModule,
    LearningSection,
)

MODULE_TITLE = "KYC Fundamentals for Bank Employees"

SECTIONS = [
    (
        "What KYC is for",
        "Know Your Customer (KYC) is the process through which a financial "
        "institution establishes and verifies a customer's identity and "
        "understands the customer relationship. Staff should follow the "
        "institution's approved, currently applicable procedures.",
    ),
    (
        "Customer information and due diligence",
        "Use only approved processes to collect and verify customer information. "
        "Keep records accurate, protect confidential information, and do not "
        "bypass required checks for convenience. Specific requirements depend "
        "on applicable current directions and institutional policy.",
    ),
    (
        "Exceptions and escalation",
        "If information is inconsistent, a request appears suspicious, or you "
        "are unsure how to proceed, pause and use the approved internal "
        "escalation channel. Do not invent exceptions or share customer data "
        "with unauthorized people.",
    ),
]

QUESTIONS = [
    {
        "question": "What does KYC stand for?",
        "options": [
            "Know Your Customer",
            "Keep Your Cash",
            "Know Your Currency",
            "Key Yield Calculation",
        ],
        "correct_option": 0,
        "explanation": "KYC stands for Know Your Customer.",
    },
    {
        "question": "What should staff use when verifying customer information?",
        "options": [
            "Personal judgment only",
            "Approved, currently applicable procedures",
            "An informal message from a friend",
            "An unverified online checklist",
        ],
        "correct_option": 1,
        "explanation": "Verification should follow approved, applicable procedures.",
    },
    {
        "question": "How should confidential customer information be handled?",
        "options": [
            "Shared with any colleague who asks",
            "Sent to a personal email account",
            "Protected and shared only through authorized processes",
            "Posted in a group chat",
        ],
        "correct_option": 2,
        "explanation": "Customer information should be protected and shared only through authorized processes.",
    },
    {
        "question": "What should an employee do if customer details appear inconsistent?",
        "options": [
            "Ignore the inconsistency",
            "Guess which information is correct",
            "Change the record without evidence",
            "Follow the approved escalation process",
        ],
        "correct_option": 3,
        "explanation": "Use the approved internal escalation process rather than guessing or bypassing checks.",
    },
    {
        "question": "Does this learning module replace current RBI directions or bank policy?",
        "options": [
            "Yes, it replaces all other guidance",
            "No, consult applicable current directions and approved policy",
            "Only for difficult cases",
            "Only when a manager is unavailable",
        ],
        "correct_option": 1,
        "explanation": "This is foundational learning and does not replace applicable current regulatory requirements or institutional policy.",
    },
]


def seed():
    db = SessionLocal()
    try:
        module = (
            db.query(LearningModule)
            .filter(LearningModule.title == MODULE_TITLE)
            .one_or_none()
        )
        if module is None:
            module = LearningModule(
                title=MODULE_TITLE,
                category="Compliance",
                description=(
                    "Foundational KYC concepts for bank employees. "
                    "Use current RBI directions and approved bank policy for real decisions."
                ),
                difficulty="beginner",
                estimated_minutes=15,
                status="published",
            )
            db.add(module)
            db.flush()

        if not module.sections:
            for order, (title, content) in enumerate(SECTIONS, start=1):
                module.sections.append(
                    LearningSection(
                        title=title,
                        content=content,
                        section_order=order,
                    )
                )

        assessment = (
            db.query(Assessment)
            .filter(Assessment.module_id == module.id)
            .first()
        )
        if assessment is None:
            assessment = Assessment(
                module_id=module.id,
                title="KYC Fundamentals Check",
                description="Five questions covering the learning module.",
                duration_minutes=10,
                passing_score=70,
            )
            db.add(assessment)
            db.flush()
            for order, question in enumerate(QUESTIONS, start=1):
                assessment.questions.append(
                    AssessmentQuestion(
                        question_order=order,
                        **question,
                    )
                )

        db.commit()
        print(
            f"Seeded demo module id={module.id}; "
            f"assessment id={assessment.id}. Safe to rerun."
        )
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
