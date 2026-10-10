# RBI Saathi — Regulatory Intelligence & Learning Prototype

RBI Saathi is a capstone prototype for exploring RBI regulatory material through retrieval-augmented question answering (RAG) and supporting staff learning with modules, assessments, scenarios, and progress tracking.

**Important:** This is an educational prototype, not legal advice or an authoritative source of current regulatory applicability. Users must verify relevant circulars, amendments, effective dates, and status on official RBI sources and follow their institution's approved compliance process.

## What is implemented

- **FastAPI backend** with health, document/chunk, regulatory-update, assistant, circular, and learning/assessment endpoints.
- **Document ingestion pipeline** for PDF extraction, regulatory chunking, source metadata, and embeddings.
- **RAG assistant** using multilingual E5 embeddings, retrieval, source citations, and safeguards for unsupported answers and questions about current applicability.
- **RBI discovery and ingestion CLI** with official-host checks, dry-run default, PDF and HTML content paths, duplicate checks, and embeddings for new chunks.
- **Learning and assessment APIs** with module content, assessment attempts, scoring, and progress.
- **React/Vite frontend** with dashboard, regulatory update, learning, scenario, assessment, results, Ask Saathi, progress, profile, and settings views.

Some frontend views are still prototype/UI-first and are not all wired to live backend APIs. The `/api/circulars/` endpoint currently uses in-memory storage, so entries there are not persistent across server restarts. See [known limitations](#known-limitations).

## Repository layout

```text
backend/       FastAPI app, database models/migrations, ingestion, RAG, tests
frontend/      React + Vite application
data/raw/      Local source documents used for development (may contain PDFs)
data/processed/Processed local artifacts
docs/          Discovery notes, demo script, submission checklist
docker-compose.yml
```

## Prerequisites

- Python with support for the project's dependencies
- Node.js and npm
- Docker Engine + Docker Compose plugin (or an existing PostgreSQL instance)
- PostgreSQL with the `pgvector` extension available
- An LLM provider for live Ask Saathi answers: local Ollama or an OpenRouter API key

The first embedding-model load may download `intfloat/multilingual-e5-small`; allow network access and disk space on first run.

## Local setup (Fedora/Linux)

Run commands from the repository root unless noted otherwise.

### 1. Start PostgreSQL

```bash
docker compose up -d db
```

The Compose service uses database `rbi_capstone`, user `rbi_user`, and password `rbi_password`.

### 2. Configure the backend

```bash
cd backend
python -m venv .venv-rbi
source .venv-rbi/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
```

If `.env` already exists, do not overwrite it; check that `DATABASE_URL` points to the database you intend to use. The Compose defaults are:

```dotenv
DATABASE_URL=postgresql+psycopg://rbi_user:rbi_password@localhost:5432/rbi_capstone
```

Before applying migrations, enable pgvector in the database:

```bash
cd ..
docker compose exec db psql -U rbi_user -d rbi_capstone \
  -c 'CREATE EXTENSION IF NOT EXISTS vector;'
cd backend
alembic upgrade head
```

Seed a small, idempotent KYC learning demo:

```bash
python -m app.seed_learning_demo
```

### 3. Configure the LLM provider

Choose one option in `backend/.env`.

**Local Ollama** (Ollama must be installed and running):

```dotenv
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:4b
```

Pull the model if needed:

```bash
ollama pull qwen3:4b
```

**OpenRouter:** set `LLM_PROVIDER=openrouter`, provide `OPENROUTER_API_KEY`, and set `OPENROUTER_MODEL` to a model available to your account. Never commit `.env` or API keys.

### 4. Start the backend

From `backend/`, with the virtual environment active:

```bash
uvicorn app.main:app --reload
```

- Health: http://127.0.0.1:8000/health
- API docs: http://127.0.0.1:8000/docs

### 5. Start the frontend

In a second terminal:

```bash
cd ~/Documents/rbi-capstone/frontend
npm install
npm run dev
```

Open the URL printed by Vite (normally http://localhost:5173).

## Tests and quality checks

Backend:

```bash
cd ~/Documents/rbi-capstone/backend
source .venv-rbi/bin/activate
python -m pytest -q
```

Focused RBI discovery/HTML ingestion tests:

```bash
python -m pytest tests/test_discover_rbi.py \
  tests/test_ingest_discovered_rbi.py \
  tests/test_rbi_html_content.py -q
```

Frontend production build and lint:

```bash
cd ~/Documents/rbi-capstone/frontend
npm run build
npm run lint
```

Record the actual results from your final checkout before submission; don't report a check as passing unless you ran it.

## RBI discovery and ingestion

Discovery is report-only and ingestion is dry-run by default. Start with a known official RBI circular page:

```bash
cd ~/Documents/rbi-capstone/backend
source .venv-rbi/bin/activate

python -m app.ingestion.ingest_discovered_rbi \
  --index-url 'https://www.rbi.org.in/Scripts/BS_CircularIndexDisplay.aspx?Id=12858'
```

This example is the CRR circular `RBI/2025-26/46`, dated 2025-06-06. The HTML adapter extracts the main circular and attached notification into separate retrieval chunks. It may have no separate PDF.

Only after reviewing the dry-run, tests, and database configuration should you add `--write`:

```bash
python -m app.ingestion.ingest_discovered_rbi \
  --index-url 'https://www.rbi.org.in/Scripts/BS_CircularIndexDisplay.aspx?Id=12858' \
  --write
```

A successful command should report `ingested` and a document ID. Then verify the saved document and its chunks in PostgreSQL/API and test a grounded RAG query. If the result is `duplicate`, `skipped`, or `failed`, do not describe it as ingested.

For the current discovery safeguards and limitations, see [docs/rbi-discovery.md](docs/rbi-discovery.md).

## Useful API routes

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/health` | Basic service health |
| `GET`, `POST` | `/api/circulars/` | Prototype in-memory circular endpoint |
| `GET`, `POST` | `/api/documents/` | List/create document metadata |
| `GET` | `/api/documents/{id}` | Read a document |
| `GET`, `POST` | `/api/documents/{id}/chunks` | List/create chunks |
| `POST` | `/api/assistant/query` | Ask a source-grounded question |
| `GET` | `/api/regulatory/updates` | List regulatory updates |
| `GET` | `/api/regulatory/updates/{id}` | Read one regulatory update |
| `GET` | `/api/learning/modules` | List published learning modules |
| `GET` | `/api/learning/modules/{id}` | Read module details |
| `POST` | `/api/learning/modules/{id}/progress` | Update learning progress |
| `GET` | `/api/learning/assessments` | List assessments |
| `POST` | `/api/learning/assessments/{id}/attempts` | Submit an assessment attempt |
| `GET` | `/api/learning/attempts` | List attempts |
| `GET` | `/api/learning/progress` | Read progress |

See interactive API documentation at `/docs` for exact request and response schemas.

## Known limitations and honest demo framing

- This is a capstone prototype, not a production compliance platform.
- RBI page layouts vary. Discovery and HTML extraction are conservative and must be checked against source content before writing.
- An official source URL does not itself prove that a circular remains in force. Applicability, supersession, and withdrawal require separate verification.
- The discovery workflow does not invent simplifications or automatically create a `RegulatoryUpdate` when grounded simplification data is unavailable.
- `/api/circulars/` uses in-memory storage.
- Several frontend routes are prototype views; not every screen is connected to a persistent API.
- No authentication/authorization or production deployment hardening is included.
- Live assistant answers require a working Ollama or OpenRouter configuration.
- Automated tests do not replace manual verification of the real database, embedding model, and live LLM provider.

## Demo path

Use [docs/demo-script.md](docs/demo-script.md) for a short walkthrough and [docs/submission-checklist.md](docs/submission-checklist.md) before handing in the project.
