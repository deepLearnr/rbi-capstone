# RBI Saathi demo script (6–8 minutes)

Use this as a concise live walkthrough. Keep the database and LLM provider ready before presenting.

## 1. Open the application (30 seconds)
- Start PostgreSQL, the FastAPI backend, and the Vite frontend.
- Show the dashboard and navigation.
- State clearly that this is a capstone prototype.

## 2. Show the regulatory source pipeline (1–2 minutes)
- From `backend/`, run the RBI CRR discovery dry-run:
  ```bash
  python -m app.ingestion.ingest_discovered_rbi \
    --index-url 'https://www.rbi.org.in/Scripts/BS_CircularIndexDisplay.aspx?Id=12858'
  ```
- Point out the official source URL, title, reference, publication date, and dry-run status.
- Explain that HTML content is extracted when no PDF is linked, and that the main circular and attached notification are separate chunks.
- Do not claim database ingestion unless the command actually reports `ingested` and you have verified the saved document.

## 3. Demonstrate source-grounded Q&A (1–2 minutes)
- Open Ask Saathi or use `/docs` → `POST /api/assistant/query`.
- Ask a question answerable from a document already present and embedded in the database.
- Show the returned citations/evidence.
- If evidence is insufficient, demonstrate that the assistant declines to assert an unsupported answer.
- Do not use a newly discovered but un-ingested document as the basis for the demo.

## 4. Show learning and assessment (1–2 minutes)
- Open Learning Paths and show a published module.
- Complete a short assessment if seeded and available.
- Show score/progress only if it is actually persisted by the running backend.

## 5. Demonstrate the regulatory email digest (1 minute)
- From `backend/`, run `python -m scripts.send_daily_digest --limit 10` to preview the message. Preview mode does not send email.
- Inspect the titles, dates, simplification fields, and official RBI source URLs; the message explicitly warns that source provenance does not prove current applicability.
- Only if SMTP has been configured and tested, run `python -m scripts.send_daily_digest --send` and show the received email. Claim delivery only after checking the recipient mailbox. See [daily-digest setup](daily-digest.md).
- State that scheduling is external to the application and that the digest currently includes the latest stored records, not only records published since the previous delivery.

## 6. Close with limitations (30 seconds)
- Explain that source-grounded retrieval and conservative uncertainty handling are the core safety goals.
- Mention that current legal applicability still requires official-source verification.
- Be transparent that some UI pages are prototype views, scenario progress is browser-local, and authentication and automatic scheduling are not implemented in the prototype.

## Backup plan
If the live LLM provider is unavailable, use `/health`, `/docs`, the discovery dry-run, and the automated test result. Do not fabricate a successful answer or persistence result.
