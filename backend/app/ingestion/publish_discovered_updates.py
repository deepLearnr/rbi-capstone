"""Create regulatory-update records for already-ingested RBI circulars.

The command is dry-run by default. Use --write to persist only simplifications
that have supported evidence and citations tied to the target document.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date

from app.db.session import SessionLocal
from app.models.document import Document
from app.models.regulatory_update import RegulatoryUpdate
from app.rag.simplification import simplify_regulation


def category_for_document(title: str, department: str | None = None) -> str:
    text = f"{title or ''} {department or ''}".lower()

    if any(term in text for term in ("cyber", "information security", "it security")):
        return "Cyber Security"
    if any(term in text for term in ("digital", "payment", "upi", "fintech")):
        return "Digital"
    if any(term in text for term in ("kyc", "anti-money laundering", "aml", "compliance")):
        return "Compliance"
    if any(term in text for term in ("risk", "capital adequacy", "crr", "slr", "liquidity")):
        return "Risk"
    return "Banking"


def build_update_payload(
    document, result, *, today: date | None = None
) -> tuple[dict | None, str]:
    """Validate simplification output before allowing it into the update feed.

    Older circulars are explicitly labeled as historical references in the
    executive summary. This does not infer or assert their current applicability.
    """
    if getattr(result, "evidence_status", None) != "supported":
        return None, "simplification evidence is insufficient"

    citations = getattr(result, "citations", None) or []
    if not citations:
        return None, "simplification has no citations"

    for citation in citations:
        title = citation.get("document_title")
        reference = citation.get("rbi_reference")
        source_url = citation.get("source_url")
        same_document = (
            title == document.title
            or (
                document.rbi_reference
                and reference == document.rbi_reference
            )
        )
        if not same_document:
            return None, "citation does not match the target document"
        if document.source_url and source_url and source_url != document.source_url:
            return None, "citation source URL does not match the target document"

    simplification = getattr(result, "simplification", None)
    if simplification is None:
        return None, "simplification payload is missing"

    if hasattr(simplification, "model_dump"):
        simplification_data = simplification.model_dump(mode="json")
    elif isinstance(simplification, dict):
        simplification_data = simplification
    else:
        return None, "simplification payload has an unsupported format"

    required_fields = {
        "executive_summary",
        "what_changed",
        "why_it_matters",
        "who_is_affected",
        "what_should_i_do",
        "important_dates",
        "terminology",
    }
    if not required_fields.issubset(simplification_data):
        return None, "simplification is missing required fields"

    summary = simplification_data.get("executive_summary")
    if not isinstance(summary, str) or not summary.strip():
        return None, "simplification has no executive summary"

    today = today or date.today()
    publication_date = document.publication_date
    if publication_date is not None and publication_date < today:
        published_label = publication_date.strftime("%-d %B %Y")
        historical_note = (
            f"Historical source note — published {published_label}. "
            "This summary describes the circular's stated provisions; it does "
            "not establish whether later RBI directions changed their current "
            "applicability. Verify subsequent applicable RBI directions before "
            "relying on it for current compliance.\n\n"
        )
        simplification_data = dict(simplification_data)
        simplification_data["executive_summary"] = historical_note + summary

    return {
        "document_id": document.id,
        "title": document.title,
        "category": category_for_document(document.title, document.department),
        "publication_date": document.publication_date,
        "effective_date": None,
        "importance": None,
        "simplification": simplification_data,
    }, "ready"


def publish_pending_updates(*, write: bool = False) -> dict[str, int]:
    counts: Counter[str] = Counter()
    with SessionLocal() as session:
        documents = (
            session.query(Document)
            .outerjoin(
                RegulatoryUpdate,
                RegulatoryUpdate.document_id == Document.id,
            )
            .filter(
                Document.document_type == "regulatory_circular",
                RegulatoryUpdate.id.is_(None),
            )
            .order_by(Document.publication_date.desc(), Document.id.desc())
            .all()
        )

        if not documents:
            print("No ingested RBI circulars are missing regulatory updates.")
            return {"ready": 0, "created": 0, "skipped": 0, "failed": 0}

        for document in documents:
            reference = document.rbi_reference or f"document id {document.id}"
            try:
                result = simplify_regulation(
                    (
                        "Create a source-grounded regulatory simplification for "
                        f"RBI circular {reference}: {document.title}. "
                        "Use only the supplied document evidence."
                    ),
                    document_id=document.id,
                )
                payload, reason = build_update_payload(document, result)
                if payload is None:
                    counts["skipped"] += 1
                    print(f"SKIPPED: {reference} — {reason}")
                    continue

                counts["ready"] += 1
                if not write:
                    print(
                        f"DRY RUN: {reference} — {document.title}; "
                        "supported simplification and matching citations; "
                        "no database changes made"
                    )
                    continue

                session.add(RegulatoryUpdate(**payload))
                session.commit()
                counts["created"] += 1
                print(f"CREATED: {reference} — {document.title}")
            except Exception as exc:
                session.rollback()
                counts["failed"] += 1
                print(f"FAILED: {reference} — {type(exc).__name__}: {exc}")

    return {
        "ready": counts["ready"],
        "created": counts["created"],
        "skipped": counts["skipped"],
        "failed": counts["failed"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate regulatory-update records for ingested RBI circulars."
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Persist supported, cited simplifications. Default is dry-run.",
    )
    args = parser.parse_args()

    counts = publish_pending_updates(write=args.write)
    print(f"Summary ({'write enabled' if args.write else 'dry-run'}): {counts}")
    return 1 if counts["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
