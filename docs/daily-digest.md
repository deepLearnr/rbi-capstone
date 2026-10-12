# RBI Saathi regulatory digest (email)

RBI Saathi can generate a plain-text email digest from the regulatory-update
records currently stored in PostgreSQL and submit it through a configured SMTP
service. The digest contains the title, category, RBI reference, publication and
effective dates, verified official RBI source link when available, and the stored
seven-part simplification fields relevant to employee action.

This is an explicit CLI workflow, not a background service: it does not expose an
unauthenticated mail-sending API, it does not send automatically when the FastAPI
server starts, and it does not track a last-delivered update watermark. It lists
up to the latest 10 stored regulatory-update records by publication date, which
may include records published before today. Do not describe it as a list of only
new circulars since the previous email.

## 1. Configure SMTP

Copy the digest settings from `.env.example` into `backend/.env` and fill them
with values provided by an email service you control. Never commit the real
`.env` file or disclose an SMTP password. For a provider supporting STARTTLS:

```dotenv
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=sender@example.com
SMTP_PASSWORD=provider-issued-app-password
SMTP_FROM_EMAIL=sender@example.com
DAILY_DIGEST_TO=recipient@example.com
SMTP_USE_SSL=false
SMTP_STARTTLS=true
```

For an SMTP service requiring implicit TLS, use its documented SSL host/port,
set `SMTP_USE_SSL=true`, and set `SMTP_STARTTLS=false`. Exactly one of
`SMTP_USE_SSL` and `SMTP_STARTTLS` must be enabled; plaintext SMTP and enabling
both modes are rejected before connecting. The sender and recipient must be valid
email addresses. `DAILY_DIGEST_TO` accepts a comma-separated list;
`--to` can override it for one run.

## 2. Preview first

Run from `backend/` with the project's virtual environment activated and the
PostgreSQL database available:

```bash
python -m scripts.send_daily_digest --limit 10
```

Preview is the default. It reads stored regulatory updates, renders the email,
prints the intended recipients and **does not send**. Check the record list,
source URLs, dates, and simplifications before sending. Unset or non-official
source URLs are not presented as official links.

## 3. Send an actual message

Only after reviewing the preview and configuring a real SMTP sender and recipient:

```bash
python -m scripts.send_daily_digest --send
```

For a one-off recipient override:

```bash
python -m scripts.send_daily_digest --send --to 'evaluator@example.com'
```

The command reports that SMTP accepted the message for submission; confirm the
mail arrived in the destination mailbox before claiming successful delivery in a
demo. Provider acceptance alone does not prove inbox delivery. SMTP exceptions or
refused recipients are reported as failures. The script does not log SMTP
credentials.

## 4. Optional daily schedule

Scheduling belongs to the deployment environment. After a successful manual send,
a host with cron can invoke the command daily, for example at 08:00 local server
time:

```cron
0 8 * * * cd /absolute/path/to/rbi-capstone/backend && /absolute/path/to/rbi-capstone/backend/.venv-rbi/bin/python -m scripts.send_daily_digest --send >> /absolute/path/to/rbi-capstone/daily-digest.log 2>&1
```

Replace paths with the actual deployment paths and ensure the service account can
read `backend/.env`. Do not configure a schedule until the recipient, provider
limits, timezone, and delivery have been tested. This repository does not create
that cron job automatically; free hosting providers may not offer a persistent
scheduler, in which case use a supported external scheduler.

## Regulatory safety

The digest is an informational summary of persisted data. An official URL proves
source provenance, not current legal applicability. The message includes this
caution and the generator only links HTTPS URLs on `rbi.org.in` or its subdomains.
Historical or withdrawn records may appear in the list and must not be presented
as current obligations without separate verification against applicable RBI
directions.
