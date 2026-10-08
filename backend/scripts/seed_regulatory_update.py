from datetime import date

from app.db.session import SessionLocal
from app.models.document import Document
from app.models.regulatory_update import RegulatoryUpdate


SIMPLIFICATION = {
    "executive_summary": (
        "The RBI amended KYC directions to extend the facility for obtaining "
        "certified copies for Foreign Portfolio Investors (FPIs), aligning them "
        "with Non-Resident Indians (NRIs) and Persons of Indian Origin (PIOs)."
    ),
    "what_changed": (
        "Banks may now obtain original certified copies for FPIs from authorized "
        "officials such as overseas branches of Scheduled Commercial Banks, "
        "Notary Public, or Indian embassies, as specified in paragraph 5(1)(v) "
        "of the amended directions."
    ),
    "why_it_matters": (
        "Not explicitly specified in the available RBI material."
    ),
    "who_is_affected": [
        "Foreign Portfolio Investors (FPIs)",
        "Non-Resident Indians (NRIs)",
        "Persons of Indian Origin (PIOs)",
    ],
    "what_should_i_do": [
        "No specific implementation action is explicitly specified in the available RBI material."
    ],
    "important_dates": [
        "September 18, 2026 (effective date of the amendment)"
    ],
    "terminology": [
        {
            "term": "Certified Copy",
            "meaning": (
                "A copy of an official document verified by an authorized "
                "officer through comparison with the original, as per the "
                "amended provisions."
            ),
        },
        {
            "term": "FPI",
            "meaning": (
                "Foreign Portfolio Investor, as defined in the Foreign Exchange "
                "Management (Deposit) Regulations, 2016."
            ),
        },
        {
            "term": "NRI",
            "meaning": (
                "Non-Resident Indian, as defined in the Foreign Exchange "
                "Management (Deposit) Regulations, 2016."
            ),
        },
        {
            "term": "PIO",
            "meaning": (
                "Person of Indian Origin, as defined in the Foreign Exchange "
                "Management (Deposit) Regulations, 2016."
            ),
        },
    ],
}


def main() -> None:
    db = SessionLocal()

    try:
        document = (
            db.query(Document)
            .filter(Document.source_file == "KYC_Rule_Commercial.pdf")
            .one_or_none()
        )

        if document is None:
            raise RuntimeError(
                "KYC_Rule_Commercial.pdf document was not found."
            )

        existing = (
            db.query(RegulatoryUpdate)
            .filter(RegulatoryUpdate.document_id == document.id)
            .one_or_none()
        )

        if existing is not None:
            print(
                f"RegulatoryUpdate already exists: "
                f"id={existing.id}, document_id={existing.document_id}"
            )
            return

        update = RegulatoryUpdate(
            document_id=document.id,
            title=document.title,
            category="Compliance",
            publication_date=document.publication_date,
            effective_date=date(2026, 9, 18),
            importance=None,
            simplification=SIMPLIFICATION,
        )

        db.add(update)
        db.commit()
        db.refresh(update)

        print(
            f"Created RegulatoryUpdate: "
            f"id={update.id}, document_id={update.document_id}"
        )

    finally:
        db.close()


if __name__ == "__main__":
    main()
