import smtplib
from datetime import date, datetime, timezone
from email.message import EmailMessage
from types import SimpleNamespace

import pytest

from app.notifications import daily_digest


@pytest.fixture
def sample_item():
    return daily_digest.DigestItem(
        title="Sample RBI circular",
        category="Compliance",
        publication_date=date(2026, 10, 1),
        effective_date=date(2026, 10, 1),
        rbi_reference="RBI/2026-27/1",
        source_url="https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=1",
        simplification={
            "executive_summary": "A verified source summary.",
            "what_changed": "The source describes a change.",
            "why_it_matters": "The change may affect bank operations.",
            "who_is_affected": ["Affected teams"],
            "what_should_i_do": ["Review the official direction."],
            "important_dates": ["2026-10-01"],
            "terminology": [{"term": "CRR", "meaning": "Cash Reserve Ratio"}],
        },
    )


def test_render_digest_includes_source_traceability_and_applicability_caution(sample_item):
    subject, body = daily_digest.render_digest(
        [sample_item],
        generated_at=datetime(2026, 10, 12, 8, 0, tzinfo=timezone.utc),
    )

    assert subject == "RBI Saathi regulatory digest — 2026-10-12"
    assert sample_item.title in body
    assert sample_item.rbi_reference in body
    assert sample_item.source_url in body
    assert "A verified source summary." in body
    assert "CRR: Cash Reserve Ratio" in body
    assert "These are not necessarily updates published today." in body
    assert "provenance, not current applicability" in body


def test_render_digest_omits_non_official_source_url(sample_item):
    unsafe = daily_digest.DigestItem(
        **{**sample_item.__dict__, "source_url": "https://rbi.org.in.attacker.example/fake"}
    )
    _, body = daily_digest.render_digest([unsafe])
    assert unsafe.source_url not in body
    assert "failed RBI-host validation" in body


def test_render_empty_digest_does_not_claim_updates_were_found():
    _, body = daily_digest.render_digest([])
    assert "No regulatory-update records are currently stored" in body
    assert "not necessarily updates published today" in body


@pytest.mark.parametrize(
    "value",
    ["", "not-an-email", "user@example.com\nBcc: attacker@example.com"],
)
def test_rejects_invalid_or_header_injected_recipients(value):
    with pytest.raises(ValueError, match="valid email address"):
        daily_digest._parse_addresses(value, field_name="recipient")


def test_send_uses_starttls_authentication_and_plain_text_message(monkeypatch):
    settings = SimpleNamespace(
        smtp_host="smtp.example.com",
        smtp_port=587,
        smtp_from_email="sender@example.com",
        daily_digest_to="one@example.com, two@example.com",
        smtp_username="sender@example.com",
        smtp_password="app-password",
        smtp_use_ssl=False,
        smtp_starttls=True,
    )
    monkeypatch.setattr(daily_digest, "get_settings", lambda: settings)
    seen = {"events": []}

    class FakeSMTP:
        def __init__(self, host, port, timeout):
            seen["connection"] = (host, port, timeout)

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def starttls(self, context):
            seen["events"].append("starttls")
            seen["tls_context"] = context

        def login(self, username, password):
            seen["events"].append("login")
            seen["credentials"] = (username, password)

        def send_message(self, message: EmailMessage):
            seen["events"].append("send")
            seen["message"] = message
            return {}

    monkeypatch.setattr(daily_digest.smtplib, "SMTP", FakeSMTP)

    result = daily_digest.send_digest_email("Digest subject", "Digest body")

    assert result == 2
    assert seen["events"] == ["starttls", "login", "send"]
    assert seen["message"]["To"] == "one@example.com, two@example.com"
    assert seen["message"].get_content().strip() == "Digest body"
    assert seen["credentials"] == ("sender@example.com", "app-password")


def test_send_fails_before_connecting_if_sender_is_not_configured(monkeypatch):
    settings = SimpleNamespace(
        smtp_host="smtp.example.com",
        smtp_port=587,
        smtp_from_email="",
        daily_digest_to="recipient@example.com",
        smtp_username="",
        smtp_password="",
        smtp_use_ssl=False,
        smtp_starttls=True,
    )
    monkeypatch.setattr(daily_digest, "get_settings", lambda: settings)
    monkeypatch.setattr(
        daily_digest.smtplib,
        "SMTP",
        lambda *_args, **_kwargs: pytest.fail("SMTP must not be contacted"),
    )

    with pytest.raises(ValueError, match="SMTP_FROM_EMAIL"):
        daily_digest.send_digest_email("Digest subject", "Digest body")


def test_send_rejects_plaintext_transport_even_without_authentication(monkeypatch):
    settings = SimpleNamespace(
        smtp_host="smtp.example.com",
        smtp_port=25,
        smtp_from_email="sender@example.com",
        daily_digest_to="recipient@example.com",
        smtp_username="",
        smtp_password="",
        smtp_use_ssl=False,
        smtp_starttls=False,
    )
    monkeypatch.setattr(daily_digest, "get_settings", lambda: settings)
    monkeypatch.setattr(
        daily_digest.smtplib,
        "SMTP",
        lambda *_args, **_kwargs: pytest.fail("SMTP must not be contacted"),
    )

    with pytest.raises(ValueError, match="SMTP transport requires TLS"):
        daily_digest.send_digest_email("Digest subject", "Digest body")


def test_send_rejects_both_tls_modes_enabled_before_connecting(monkeypatch):
    settings = SimpleNamespace(
        smtp_host="smtp.example.com",
        smtp_port=465,
        smtp_from_email="sender@example.com",
        daily_digest_to="recipient@example.com",
        smtp_username="",
        smtp_password="",
        smtp_use_ssl=True,
        smtp_starttls=True,
    )
    monkeypatch.setattr(daily_digest, "get_settings", lambda: settings)
    monkeypatch.setattr(
        daily_digest.smtplib,
        "SMTP_SSL",
        lambda *_args, **_kwargs: pytest.fail("SMTP must not be contacted"),
    )

    with pytest.raises(ValueError, match="exactly one SMTP TLS mode"):
        daily_digest.send_digest_email("Digest subject", "Digest body")


def test_cli_previews_by_default_and_does_not_send(monkeypatch, capsys, sample_item):
    from scripts import send_daily_digest as cli

    monkeypatch.setattr(cli, "load_digest_items", lambda limit: [sample_item])
    monkeypatch.setattr(cli, "render_digest", lambda *_args, **_kwargs: ("Preview subject", "Preview body\n"))
    monkeypatch.setattr(
        cli,
        "get_settings",
        lambda: SimpleNamespace(daily_digest_to="recipient@example.com"),
    )
    monkeypatch.setattr(
        cli,
        "send_digest_email",
        lambda *_args, **_kwargs: pytest.fail("Preview mode must not send email"),
    )

    assert cli.main([]) == 0
    output = capsys.readouterr().out
    assert "PREVIEW ONLY" in output
    assert "recipient@example.com" in output
    assert "Preview body" in output


def test_cli_sends_only_when_send_flag_is_supplied(monkeypatch, capsys, sample_item):
    from scripts import send_daily_digest as cli

    monkeypatch.setattr(cli, "load_digest_items", lambda limit: [sample_item])
    monkeypatch.setattr(cli, "render_digest", lambda *_args, **_kwargs: ("Send subject", "Send body\n"))
    calls = {}

    def fake_send(subject, body, *, recipient_override=None):
        calls.update(subject=subject, body=body, recipient_override=recipient_override)
        return 1

    monkeypatch.setattr(cli, "send_digest_email", fake_send)

    assert cli.main(["--send", "--to", "evaluator@example.com"]) == 0
    output = capsys.readouterr().out
    assert "SMTP accepted" in output
    assert calls["subject"] == "Send subject"
    assert calls["recipient_override"] == "evaluator@example.com"


def test_cli_does_not_print_raw_smtp_exception_response(monkeypatch, capsys, sample_item):
    from scripts import send_daily_digest as cli

    monkeypatch.setattr(cli, "load_digest_items", lambda limit: [sample_item])
    monkeypatch.setattr(cli, "render_digest", lambda *_args, **_kwargs: ("subject", "body\n"))

    def fail_send(*_args, **_kwargs):
        raise smtplib.SMTPAuthenticationError(
            535,
            b"authentication failed; diagnostic=DO_NOT_PRINT_THIS_SECRET",
        )

    monkeypatch.setattr(cli, "send_digest_email", fail_send)

    assert cli.main(["--send"]) == 2
    captured = capsys.readouterr()
    assert "SMTP delivery error (SMTPAuthenticationError)" in captured.err
    assert "DO_NOT_PRINT_THIS_SECRET" not in captured.err
