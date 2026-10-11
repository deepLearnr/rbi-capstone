"""Audit and safely repair existing regulatory-update metadata.

Dry-run by default. Use --write to persist deterministic repairs. The KYC URL
must be supplied only after independently verifying the exact official RBI page.
"""
from __future__ import annotations

import argparse

from sqlalchemy.orm import joinedload

from app.db.session import SessionLocal
from app.models.regulatory_update import RegulatoryUpdate
from app.ingestion.regulatory_maintenance import (
    historicalize_crr_simplification,
    validate_official_rbi_url,
)


def maintain(*, write: bool = False, kyc_source_url: str | None = None) -> dict[str, int]:
    counts = {"checked": 0, "missing_source_url": 0, "summary_candidates": 0, "repairs_applied": 0}
    validated_url = validate_official_rbi_url(kyc_source_url) if kyc_source_url else None

    with SessionLocal() as session:
        updates = (
            session.query(RegulatoryUpdate)
            .options(joinedload(RegulatoryUpdate.document))
            .order_by(RegulatoryUpdate.id)
            .all()
        )
        for update in updates:
            counts["checked"] += 1
            document = update.document
            ref = document.rbi_reference or f"document_id={document.id}"

            if not document.source_url:
                counts["missing_source_url"] += 1
                if ref == "RBI/2026-27/257" and validated_url:
                    document.source_url = validated_url
                    if write:
                        counts["repairs_applied"] += 1
                    print(f"{'REPAIR' if write else 'WOULD REPAIR'} source URL: {ref}")
                else:
                    print(f"MISSING SOURCE URL: {ref} ({document.source_file or 'no source file'})")
            elif ref == "RBI/2026-27/257" and validated_url and document.source_url != validated_url:
                raise ValueError(
                    "Refusing to overwrite an existing KYC source URL. "
                    "Inspect the current URL and verify the replacement manually."
                )

            if ref == "RBI/2025-26/46":
                revised, changed = historicalize_crr_simplification(update.simplification)
                if changed:
                    counts["summary_candidates"] += 1
                    print(f"{'REPAIR' if write else 'WOULD REPAIR'} historical wording: {ref}")
                    if write:
                        update.simplification = revised
                        counts["repairs_applied"] += 1

        if write and counts["repairs_applied"]:
            session.commit()
        else:
            session.rollback()

    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Persist proposed repairs; default is dry-run.")
    parser.add_argument(
        "--kyc-source-url",
        help="Exact official RBI URL verified for RBI/2026-27/257; never guessed by this script.",
    )
    args = parser.parse_args()
    counts = maintain(write=args.write, kyc_source_url=args.kyc_source_url)
    print(f"Summary ({'write enabled' if args.write else 'dry-run'}): {counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
