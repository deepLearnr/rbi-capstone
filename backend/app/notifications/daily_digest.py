"""Preview and send a source-grounded digest of stored RBI regulatory updates.

This module deliberately sends only on an explicit call from the CLI. It does
not expose an unauthenticated HTTP endpoint or claim that a circular remains in
force merely because an official source URL is available.
"""
from __future__ import annotations

import re
import smtplib
import ssl
from dataclasses import dataclass
from datetime import date, datetime
from email.message import EmailMessage
from email.utils import getaddresses, parseaddr
from typing import Any, Sequence

from app.core.config import get_settings
from app.ingestion.regulatory_maintenance import validate_official_rbi_url

EMAIL_PATTERN = re.compile(r"^[^@\s,<>]+@[^@\s,<>]+\.[^@\s,<>]+$")
MAX_DIGEST_ITEMS = 50


@dataclass(frozen=True)
class DigestItem:
    title: str
    category: str
    publication_date: date | None
    effective_date: date | None
    rbi_reference: str | None
    source_url: str | None
    simplification: dict[str, Any]


def load_digest_items(limit: int = 10) -> list[DigestItem]:
    """Load the latest stored update records without modifying the database."""
    if not 1 <= limit <= MAX_DIGEST_ITEMS:
        raise ValueError(f"limit must be between 1 and {MAX_DIGEST_ITEMS}.")

    # Import models only for the database operation. Rendering and sending
    # functions remain independently testable without opening a DB connection.
    from sqlalchemy.orm import joinedload

    from app.db.session import SessionLocal
    from app import models

    with SessionLocal() as session:
        updates = (
            session.query(models.RegulatoryUpdate)
            .options(joinedload(models.RegulatoryUpdate.document))
            .order_by(
                models.RegulatoryUpdate.publication_date.desc().nulls_last(),
                models.RegulatoryUpdate.id.desc(),
            )
            .limit(limit)
            .all()
        )
        return [
            DigestItem(
                title=update.title,
                category=update.category,
                publication_date=update.publication_date,
                effective_date=update.effective_date,
                rbi_reference=update.document.rbi_reference,
                source_url=update.document.source_url,
                simplification=dict(update.simplification or {}),
            )
            for update in updates
        ]


def _format_date(value: date | str | None) -> str:
    return value.isoformat() if value else "Not specified"


def _format_bullets(value: Any) -> str:
    if not isinstance(value, (list, tuple)):
        return "- Not specified in the stored simplification."
    lines = [str(item).strip() for item in value if str(item).strip()]
    if not lines:
        return "- Not specified in the stored simplification."
    return "\n".join(f"- {line}" for line in lines)


def _format_terminology(value: Any) -> str:
    if not isinstance(value, (list, tuple)):
        return "- Not specified in the stored simplification."
    entries = []
    for item in value:
        if isinstance(item, dict):
            term = str(item.get("term", "")).strip()
            meaning = str(item.get("meaning", "")).strip()
            if term and meaning:
                entries.append(f"- {term}: {meaning}")
    return "\n".join(entries) if entries else "- Not specified in the stored simplification."


def _source_line(source_url: str | None) -> str:
    if not source_url:
        return "Official source: Not recorded in stored metadata."
    try:
        verified_url = validate_official_rbi_url(source_url)
    except ValueError:
        return "Official source: Link omitted because the stored URL failed RBI-host validation."
    return f"Official source: {verified_url}"


def render_digest(
    items: Sequence[DigestItem],
    *,
    generated_at: datetime | None = None,
) -> tuple[str, str]:
    """Return an email subject and plain-text body for the supplied records."""
    timestamp = generated_at or datetime.now().astimezone()
    if timestamp.tzinfo is None:
        timestamp = timestamp.astimezone()
    subject = f"RBI Saathi regulatory digest — {timestamp.date().isoformat()}"

    lines = [
        "RBI Saathi — Regulatory Updates Digest",
        f"Generated: {timestamp.isoformat(timespec='minutes')}",
        "",
        (
            "Scope: the latest regulatory-update records stored in RBI Saathi. "
            "These are not necessarily updates published today."
        ),
        (
            "Regulatory caution: a source link establishes provenance, not current "
            "applicability. Verify later RBI directions and the source's current "
            "status before making compliance decisions."
        ),
        "",
    ]

    if not items:
        lines.append("No regulatory-update records are currently stored in RBI Saathi.")
        return subject, "\n".join(lines).strip() + "\n"

    for index, item in enumerate(items, start=1):
        simplification = item.simplification or {}
        lines.extend(
            [
                "=" * 72,
                f"{index}. {item.title}",
                f"Category: {item.category or 'Not specified'}",
                f"RBI reference: {item.rbi_reference or 'Not recorded'}",
                f"Publication date: {_format_date(item.publication_date)}",
                f"Effective date: {_format_date(item.effective_date)}",
                _source_line(item.source_url),
                "",
                "Executive summary:",
                str(
                    simplification.get("executive_summary")
                    or "Not specified in the stored simplification."
                ),
                "",
                "What changed:",
                str(
                    simplification.get("what_changed")
                    or "Not specified in the stored simplification."
                ),
                "",
                "Why it matters:",
                str(
                    simplification.get("why_it_matters")
                    or "Not specified in the stored simplification."
                ),
                "",
                "Who is affected:",
                _format_bullets(simplification.get("who_is_affected")),
                "",
                "Suggested actions recorded in the simplification:",
                _format_bullets(simplification.get("what_should_i_do")),
                "",
                "Important dates recorded in the simplification:",
                _format_bullets(simplification.get("important_dates")),
                "",
                "Terminology:",
                _format_terminology(simplification.get("terminology")),
                "",
            ]
        )

    lines.extend(
        [
            "=" * 72,
            "This digest is an informational summary of records stored in RBI Saathi, not legal advice.",
            "Confirm requirements, supersession, withdrawal, and effective dates against official RBI directions.",
        ]
    )
    return subject, "\n".join(lines).strip() + "\n"


def _parse_addresses(value: str, *, field_name: str) -> list[str]:
    if not value or "\r" in value or "\n" in value:
        raise ValueError(f"{field_name} must contain valid email address(es).")
    parsed = getaddresses([value])
    addresses = [address.strip() for _, address in parsed if address.strip()]
    if not addresses or any(
        not EMAIL_PATTERN.fullmatch(address) for address in addresses
    ):
        raise ValueError(f"{field_name} must contain valid email address(es).")
    # Normalize and de-duplicate without changing the order supplied by the user.
    return list(dict.fromkeys(addresses))


def send_digest_email(
    subject: str,
    body: str,
    *,
    recipient_override: str | None = None,
) -> int:
    """Submit a digest email using SMTP settings from the environment/.env."""
    settings = get_settings()
    host = str(settings.smtp_host or "").strip()
    sender_value = str(settings.smtp_from_email or "").strip()
    recipient_value = recipient_override or settings.daily_digest_to or ""

    if (
        not host
        or any(character.isspace() for character in host)
        or any(character in host for character in "\r\n")
    ):
        raise ValueError("SMTP_HOST must be configured with a valid SMTP hostname.")
    if not 1 <= int(settings.smtp_port) <= 65535:
        raise ValueError("SMTP_PORT must be between 1 and 65535.")
    if not subject or "\r" in subject or "\n" in subject:
        raise ValueError("Email subject must be non-empty and contain no newlines.")

    if "\r" in sender_value or "\n" in sender_value:
        raise ValueError("SMTP_FROM_EMAIL must be a valid email address.")
    sender = parseaddr(sender_value)[1]
    if not sender or not EMAIL_PATTERN.fullmatch(sender):
        raise ValueError("SMTP_FROM_EMAIL must be a valid email address.")
    recipients = _parse_addresses(recipient_value, field_name="DAILY_DIGEST_TO / --to")

    username = str(settings.smtp_username or "").strip()
    password = str(settings.smtp_password or "")
    if bool(username) != bool(password):
        raise ValueError("SMTP_USERNAME and SMTP_PASSWORD must be configured together.")

    use_ssl = bool(settings.smtp_use_ssl)
    use_starttls = bool(settings.smtp_starttls)
    if use_ssl and use_starttls:
        raise ValueError(
            "Configure exactly one SMTP TLS mode: SMTP_USE_SSL or SMTP_STARTTLS."
        )
    if not use_ssl and not use_starttls:
        raise ValueError(
            "SMTP transport requires TLS; enable SMTP_STARTTLS or SMTP_USE_SSL."
        )

    message = EmailMessage()
    message["From"] = sender
    message["To"] = ", ".join(recipients)
    message["Subject"] = subject
    message.set_content(body)

    def deliver(connection: Any) -> None:
        if not use_ssl and use_starttls:
            connection.starttls(context=ssl.create_default_context())
        if username:
            connection.login(username, password)
        refused = connection.send_message(message)
        if refused:
            raise RuntimeError(f"SMTP refused {len(refused)} digest recipient(s).")

    if use_ssl:
        with smtplib.SMTP_SSL(
            host,
            int(settings.smtp_port),
            timeout=20,
            context=ssl.create_default_context(),
        ) as connection:
            deliver(connection)
    else:
        with smtplib.SMTP(host, int(settings.smtp_port), timeout=20) as connection:
            deliver(connection)

    return len(recipients)
