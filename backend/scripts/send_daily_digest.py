"""Preview or explicitly send the stored RBI regulatory-update digest.

Run from backend/ with the project's environment configured:
    python -m scripts.send_daily_digest
    python -m scripts.send_daily_digest --send
"""
from __future__ import annotations

import argparse
import smtplib
import sys
from datetime import datetime

from app.core.config import get_settings
from app.notifications.daily_digest import (
    load_digest_items,
    render_digest,
    send_digest_email,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--send",
        action="store_true",
        help="Actually submit the email through SMTP. Without this flag, only preview is printed.",
    )
    parser.add_argument(
        "--to",
        help="Override DAILY_DIGEST_TO for this run; supports comma-separated email addresses.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of most-recent stored update records to include (1–50; default: 10).",
    )
    args = parser.parse_args(argv)

    try:
        items = load_digest_items(limit=args.limit)
        generated_at = datetime.now().astimezone()
        subject, body = render_digest(items, generated_at=generated_at)

        if args.send:
            count = send_digest_email(subject, body, recipient_override=args.to)
            print(
                f"SMTP accepted the digest for {count} recipient(s). "
                "Verify receipt in the destination mailbox."
            )
            return 0

        settings = get_settings()
        intended_recipient = args.to or settings.daily_digest_to or "not configured"
        print("PREVIEW ONLY — no email was sent.")
        print(f"Intended recipient(s): {intended_recipient}")
        print(f"Subject: {subject}\n")
        print(body, end="")
        print("\nTo send after reviewing and configuring SMTP, rerun with --send.")
        return 0
    except smtplib.SMTPException as exc:
        # SMTP server replies can contain provider-controlled text. Do not echo
        # raw responses; report the exception class without exposing credentials.
        print(
            f"Daily digest failed: SMTP delivery error ({type(exc).__name__}).",
            file=sys.stderr,
        )
        return 2
    except (ValueError, RuntimeError, OSError) as exc:
        print(f"Daily digest failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
