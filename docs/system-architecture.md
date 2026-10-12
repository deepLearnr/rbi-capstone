# RBI Saathi system architecture

Status: documentation of the implementation reviewed on 12 October 2026. Treat behavior described as implemented only where a code path or endpoint exists; otherwise it is identified as a gap or limitation.

## Component architecture

```mermaid
flowchart LR
    U[Employee / evaluator browser]
    FE[React 19 + Vite static frontend]
    API[FastAPI application]
    RAG[RAG orchestration and guardrails]
    EMB[Sentence Transformers\nintfloat/multilingual-e5-small\n384-d embeddings]
    LLM[Configured LLM provider\nOllama or OpenRouter]
    DB[(PostgreSQL + pgvector)]
    RBI[Official RBI HTML / PDF sources]
    DISC[Discovery and ingestion CLI]
    PUB[Grounded simplification publisher CLI]
    DIG[Daily digest CLI]
    SMTP[Configured SMTP server]
    LS[(Browser localStorage)]

    U --> FE
    FE -->|JSON over HTTP(S)\nVITE_API_BASE_URL| API
    API --> RAG
    RAG --> EMB
    EMB -->|384-d query embedding| DB
    DB -->|top-k chunks by cosine distance| RAG
    RAG -->|context + evidence IDs| LLM
    LLM -->|status, evidence IDs, answer| RAG
    RAG -->|validated answer + citations| API
    API <--> DB

    RBI --> DISC
    DISC -->|verified PDF / HTML, chunks, embeddings| DB
    DB --> PUB
    PUB -->|seven-part simplification after review| DB
    DB --> DIG
    DIG -->|preview or explicit SMTP send| SMTP
    FE <--> LS
```

## Runtime components and responsibilities

- **Frontend:** React with Vite and React Router. `VITE_API_BASE_URL` selects the FastAPI origin at build time. Regulatory updates, Ask Saathi, learning modules, assessments and learning progress have API client paths. Scenario questions are stored in `frontend/src/data/scenarios.js`; scenario attempt history and sessions are stored in browser `localStorage`, not in the API/database.
- **API:** `backend/app/main.py` registers health, circular, document, assistant, regulatory-update and learning routers. Interactive OpenAPI documentation is available at `/docs`, with the schema at `/openapi.json`.
- **Persistence:** SQLAlchemy models and Alembic migrations describe documents, chunks, regulatory updates and learning/assessment tables. `document_chunks.embedding` is `vector(384)`. The legacy `/api/circulars/` route uses in-memory process state and is not persistent.
- **Retrieval:** The query is encoded with `intfloat/multilingual-e5-small` using the `query:` prefix; ingested passages use `passage:`. The vector store selects embedded chunks by cosine distance.
- **Generation:** `app.llm.service` selects the configured Ollama or OpenRouter provider. The prompt asks for a structured evidence status, chunk IDs, and answer. The server checks returned IDs against retrieved chunks and then builds citation objects from stored metadata.
- **Ingestion:** RBI discovery produces candidates; ingestion is dry-run by default. Eligible official PDF or HTML content is extracted, chunked, embedded and written transactionally. Generating a `RegulatoryUpdate` is a separate operation and is not inferred from a discovered title alone.
- **Digest:** `python -m scripts.send_daily_digest` reads stored regulatory updates. It previews by default and only contacts SMTP when invoked with `--send` and valid configuration. It is a CLI workflow, not a scheduled service by itself.

## RAG query sequence

```mermaid
sequenceDiagram
    participant B as Browser
    participant A as FastAPI /api/assistant/query
    participant E as Embedding model
    participant D as PostgreSQL + pgvector
    participant M as Ollama / OpenRouter

    B->>A: question, top_k, role
    A->>E: embed query with query: prefix
    E-->>A: 384-dimensional vector
    A->>D: order embedded chunks by cosine distance
    D-->>A: top-k chunks + document metadata
    A->>M: prompt, context and allowed evidence IDs
    M-->>A: evidence status, IDs and answer
    A->>A: parse response; validate IDs; apply applicability guardrail
    A-->>B: answer, citations, evidence_status
```

## Ingestion and simplification sequence

1. Discover candidates from an official RBI index or inspect a known detail page.
2. Inspect dry-run metadata and extraction output.
3. On an explicit write, validate the official HTTPS host, document identity and content; extract PDF or HTML; chunk the content; compute embeddings; persist the document and chunks in a transaction.
4. Test vector retrieval and citation metadata.
5. Run the simplification publisher separately. It uses the selected document's own embedded chunks and can preview candidate seven-part `RegulatoryUpdate` records before an explicit write.
6. Verify the update and source URL through the API and browser.

## Deployment-relevant constraints

- Current CORS configuration in `backend/app/main.py` only allows `http://localhost:5173` and `http://127.0.0.1:5173`. A hosted frontend origin must be added/configurable before production frontend-to-API calls will work.
- The embedding model loads lazily on the first RAG query and may download model files if no cache exists. Cloud deployment must allow adequate RAM, startup/request time, and outbound HTTPS access.
- No backend authentication/authorization or user identity model is present. Learning progress is shared per module in the database, not per authenticated employee. Scenario progress is browser-local.
- The circulars router is in-memory. Do not present it as the persistent ingestion system.
- SMTP delivery is only a CLI workflow. For example, Render Free web services currently block outbound SMTP ports 25, 465 and 587; do not rely on SMTP delivery from that hosting plan. See [hosting assessment](hosting-assessment.md).
