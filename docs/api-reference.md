# RBI Saathi API reference

FastAPI exposes interactive documentation at `/docs` and OpenAPI JSON at `/openapi.json`. The following list is a human-readable summary of the routes registered in `backend/app/main.py`; OpenAPI is authoritative for the running build's full schemas.

Base URL examples use `http://127.0.0.1:8000` locally. Replace it with the deployed API origin when hosted.

## Health

| Method | Path | Behavior |
|---|---|---|
| `GET` | `/health` | Returns a basic service health object. It does not prove the LLM provider is ready or that every database query succeeds. |

## Documents and legacy circulars

| Method | Path | Behavior |
|---|---|---|
| `GET` | `/api/documents/` | List persisted document metadata. |
| `POST` | `/api/documents/` | Create document metadata. This CRUD route does not perform the PDF/HTML ingestion pipeline or compute embeddings. |
| `GET` | `/api/documents/{document_id}` | Get one document; 404 when absent. |
| `GET` | `/api/documents/{document_id}/chunks` | List chunks in chunk-index order. |
| `POST` | `/api/documents/{document_id}/chunks` | Create a chunk under an existing document. This route stores supplied chunk fields; it does not itself compute an embedding. |
| `GET` | `/api/circulars/` | List legacy in-memory circular records. Data is lost on process restart and is separate from the persistent document pipeline. |
| `POST` | `/api/circulars/` | Add a legacy in-memory circular. Not a persistent ingestion endpoint. |

Document creation requires `title` and `document_type`. Optional fields include `rbi_reference`, `publication_date`, `department`, `source_url`, `source_file`, `language`, and `description`. Chunk creation requires `chunk_index` and `content`; page, section, heading, path and JSON metadata fields are optional.

## RAG assistant

| Method | Path | Behavior |
|---|---|---|
| `POST` | `/api/assistant/query` | Retrieve similar embedded chunks, call the configured LLM, validate evidence IDs, and return an answer with citations and evidence status. |

Example request:

```json
{
  "question": "What did RBI circular RBI/2025-26/46 state?",
  "top_k": 3,
  "role": "bank_employee"
}
```

`role` may be `bank_employee`, `compliance_officer`, `branch_manager`, or `customer_support`. The response schema is `{ "answer": "...", "citations": [...], "evidence_status": "supported|insufficient" }`. A current-applicability question is returned as insufficient unless every cited chunk has verified `active` status metadata. This is a conservative metadata guardrail, not a complete legal-status lookup.

## Regulatory updates

| Method | Path | Behavior |
|---|---|---|
| `GET` | `/api/regulatory/updates` | List persisted regulatory updates ordered by publication date and ID. |
| `GET` | `/api/regulatory/updates/{update_id}` | Read a single update, including its seven-part simplification and linked document metadata; 404 when absent. |

The simplification contains `executive_summary`, `what_changed`, `why_it_matters`, `who_is_affected`, `what_should_i_do`, `important_dates`, and `terminology`.

## Learning and assessments

| Method | Path | Behavior |
|---|---|---|
| `GET` | `/api/learning/modules` | List published modules and summary/progress fields. |
| `GET` | `/api/learning/modules/{module_id}` | Get module sections and assessment summaries. |
| `POST` | `/api/learning/modules/{module_id}/progress` | Update the module progress percentage (`progress_percent`, integer 0–100). |
| `POST` | `/api/learning/modules/{module_id}/sections/{section_id}/progress` | Mark a module section complete/incomplete (`completed`, boolean) and recalculate progress. |
| `GET` | `/api/learning/assessments` | List assessment summaries. |
| `GET` | `/api/learning/assessments/{assessment_id}` | Read the assessment and question/options. Correct answers/explanations are withheld until submission. |
| `POST` | `/api/learning/assessments/{assessment_id}/attempts` | Submit `answers`, each with `question_id` and optional `selected_option`; returns persisted score/attempt details. |
| `GET` | `/api/learning/attempts` | List persisted assessment attempts. |
| `GET` | `/api/learning/progress` | Return module progress and aggregate assessment metrics. |

**Identity limitation:** there is no authentication or user ID in these contracts. Learning progress and assessment attempts are shared demo data rather than separated by employee. Scenario category questions/attempts are not exposed by these API routes; the frontend scenario catalog and attempt history are static/browser-local.

## Operational interfaces not exposed as public API routes

RBI discovery/ingestion, generation of regulatory-update records, and email digest delivery are CLI workflows. See `docs/rbi-discovery.md`, `docs/regulatory-maintenance.md`, and `docs/daily-digest.md`. The digest is preview-only unless explicitly run with `--send`; it does not have a public mail-sending endpoint or a scheduler provisioned by the application.

## Security warning

The code reviewed does not include backend authentication/authorization. Do not treat the CRUD or learning mutation routes as a production-secure public API. A public demonstration needs access controls or other deployment-level restrictions appropriate to its intended exposure.
