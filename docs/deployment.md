# Backend container deployment

This guide packages the FastAPI API as a container. It does **not** deploy the frontend, provision PostgreSQL, seed RBI source documents, or create embeddings. Complete those separately and verify them before sharing a public demo URL.

## Runtime requirements

- A PostgreSQL database with `pgvector` enabled and network access from the API service.
- A database URL supplied as `DATABASE_URL`, using the `postgresql+psycopg://` driver form.
- An LLM provider configured through environment variables. For a hosted deployment, use `LLM_PROVIDER=openrouter` and store `OPENROUTER_API_KEY` as a platform secret. The default Ollama URL points to localhost and is not a hosted Ollama deployment.
- The exact public frontend origin in `CORS_ORIGINS`. Use a comma-separated list with no trailing path, for example `https://rbi-saathi.pages.dev,https://app.example.org`.

Do not add credentials to the Dockerfile, image, Git history, frontend build variables, or documentation. Supply secrets through the hosting platform's secret/environment mechanism.

## Build and run locally

Run from the repository root:

```bash
docker build -f backend/Dockerfile -t rbi-saathi-api .
```

For a local smoke test against the PostgreSQL container created by the repository's Compose file, configure `backend/.env` as described in the root README, then run:

```bash
docker run --rm \
  --add-host=host.docker.internal:host-gateway \
  --env-file backend/.env \
  -e DATABASE_URL='postgresql+psycopg://rbi_user:rbi_password@host.docker.internal:5432/rbi_capstone' \
  -e PORT=8080 \
  -p 8000:8080 \
  rbi-saathi-api
```

The `DATABASE_URL` override is needed because `localhost` inside a container refers to that container, not the host. This command assumes the local database port is published on the host as in `docker-compose.yml`.

In another terminal, check:

```bash
curl --fail http://127.0.0.1:8000/health
curl --fail -I http://127.0.0.1:8000/docs
```

`/health` currently confirms that the API process responds; it is not a database-readiness check. Verify database connectivity by calling a database-backed endpoint after migrations.

## Database migrations and vector extension

Run migrations as a one-off deployment step against the target database, using the same image and `DATABASE_URL` as the API:

```bash
docker run --rm \
  --env-file backend/.env \
  -e DATABASE_URL="$DATABASE_URL" \
  rbi-saathi-api \
  alembic upgrade head
```

Replace `$DATABASE_URL` with the target database URL in your deployment shell or pass it securely through your platform's one-off job mechanism. Confirm that `CREATE EXTENSION vector` is permitted by the database provider and enable it before migrations if required. Do not run schema migrations concurrently from every API replica.

## Hosted frontend and CORS

The frontend reads `VITE_API_BASE_URL` at build time, falling back to `http://127.0.0.1:8000` when it is absent. For a static hosting build, set `VITE_API_BASE_URL` to the deployed API's HTTPS URL before running `npm run build`.

On the backend, set `CORS_ORIGINS` to the frontend's exact origin, for example `https://rbi-saathi.pages.dev`. Origins include scheme and host, but no path or trailing slash. Add any custom production domain explicitly. Avoid `*`; the current middleware enables credentials, so the allowed origin list should remain specific. Preview deployment origins are not automatically allowed.

## Verification before sharing the URL

1. Build the image from the final commit, not from an older archive.
2. Configure a managed PostgreSQL/pgvector database, then apply Alembic migrations.
3. Confirm `GET /health`, `GET /api/regulatory/updates`, a document-backed route, and `POST /api/assistant/query` against the hosted service.
4. Verify the browser preflight/request from the exact deployed frontend origin, and inspect browser console/network errors.
5. Confirm the embedding model can be downloaded and loaded within the provider's memory, disk, startup, and request-time limits. It is loaded lazily on first retrieval; the first assistant query may be slower.
6. Load and verify the intended demo documents, chunk embeddings, learning data, and regulatory updates. Deploying the image does not copy the developer's local PostgreSQL volume or local corpus.
7. Use an actual configured LLM provider and test a question with citations plus a question where applicability is unknown. A successful health response alone is not a product acceptance test.

The project still lacks authentication/authorization and production-grade user isolation. Do not expose sensitive internal or customer data or represent the prototype as an authoritative compliance decision system.
