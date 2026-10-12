# Free-hosting assessment for the capstone demo

Reviewed: 12 October 2026. Provider terms and free quotas can change; re-check the linked official pages immediately before creating services. A provider's free tier is suitable for an evaluator prototype, not a production compliance application.

## Candidate topology

| Layer | Candidate | Fit and limitations |
|---|---|---|
| React/Vite frontend | [Cloudflare Pages](https://developers.cloudflare.com/pages/framework-guides/deploy-a-vite3-project/) | Static React/Vite output is suitable. Use `frontend/` as the project root, `npm run build` as build command and `dist` as output directory. Static asset requests are free on the Pages Free plan; the current limits page reports 500 builds per month and one concurrent build. |
| FastAPI + embedding inference | [Google Cloud Run](https://cloud.google.com/run/pricing) | A request-driven service can scale to zero. For request-based billing, the pricing page currently lists a monthly free tier of 180,000 vCPU-seconds, 360,000 GiB-seconds, and 2 million requests; the separate instance-based billing model has different allowances. Choose request-based billing with `min-instances=0` for the prototype. Choose a memory limit appropriate for Sentence Transformers; Cloud Run defaults to 2 GiB and allows configuring memory. A Google Cloud billing account is required and usage/region/network can exceed the free allowance. The price page says free-tier usage is aggregated across projects by billing account and is applied using Tier 1 pricing; outbound internet’s 1 GiB free transfer is documented for North America. Set a maximum instance count and billing alerts; alerts are not a hard spending cap. |
| PostgreSQL + pgvector | [Supabase Free](https://supabase.com/docs/guides/database/extensions/pgvector) | The `vector` extension is supported. Current Free plan documentation lists a 500 MB database size quota. Projects with low database activity over seven days can be paused. Test the exact migration and `vector(384)` type in a throwaway project before moving data. |

Official plan constraints to account for:

- Cloudflare Pages Vite configuration: `npm run build`, output directory `dist`. Static assets are suitable for this frontend; the browser calls the backend API separately. See [Pages limits](https://developers.cloudflare.com/pages/platform/limits/).
- Cloud Run free-tier quantities are aggregated by billing account. The published pricing page identifies Mumbai (`asia-south1`) and Delhi (`asia-south2`) regions, but do not assume every network transfer/region-specific SKU is free. See [Cloud Run pricing](https://cloud.google.com/run/pricing) and [memory limits](https://docs.cloud.google.com/run/docs/configuring/instances/memory-limits).
- Supabase Free project pausing: [official pausing policy](https://supabase.com/docs/guides/platform/free-project-pausing). The platform documents automatic pausing after a week of insufficient database activity.
- [Render Free limits](https://render.com/docs/free) and [Render compute plans](https://render.com/docs/compute-plans) are less suitable for this specific backend as a first choice: a Free web service has 512 MB RAM and 0.1 CPU, spins down after 15 minutes, and can take about a minute to restart; the documented plan also blocks outbound SMTP ports 25, 465 and 587, and its Free Postgres database expires after 30 days. This does not mean Render is unusable for every app, but the embedding model and digest SMTP make those limits material here.

## Blocking work before deployment

1. **CORS is local-only.** `backend/app/main.py` currently allows only `http://localhost:5173` and `http://127.0.0.1:5173`. Make the allowlist configurable by an environment variable and set it to the exact deployed Pages origin before attempting browser-to-API requests. Do not use wildcard origins with credentials enabled.
2. **Model memory/cold start.** `SentenceTransformer("intfloat/multilingual-e5-small")` is loaded lazily on the first embedding request. A deployed service needs outbound HTTPS to fetch weights unless they are baked into its image/cache. Measure first-query memory and latency with the real embedding model and enforce bounded instance count/timeout.
3. **Managed PostgreSQL compatibility.** Enable `vector`; check where the extension is installed and ensure Alembic can resolve the unqualified `vector(384)` type used by the model/migration. Run `alembic upgrade head` against a disposable project before importing any real rows.
4. **Preloaded demo data.** A new managed database starts empty. Migrations plus `seed_learning_demo.py` do not reconstruct the currently verified four documents, 90 embedded chunks, and two regulatory updates. Preserve/import the already-reviewed local database data using a controlled one-time data migration or create a complete idempotent seeding command. Do not commit a database dump or credentials.
5. **Public API security.** There is no authentication/authorization, and some write endpoints mutate persistent records. Restrict/guard write operations or keep the service's exposure appropriate for a capstone demo before making it publicly reachable.
6. **Digest SMTP.** Render Free blocks common SMTP ports; do not put this SMTP CLI on that plan and claim it can send. A real delivery test must use a provider/network that permits the chosen encrypted SMTP transport, and a daily cron job is not created by this repo. Preview alone does not satisfy the brief's distribution demo.
7. **LLM provider.** Ollama on a local laptop is not reachable from a hosted backend unless separately exposed securely. For a hosted demo, configure a valid remote OpenRouter-compatible provider or deploy Ollama separately; keep API keys in platform secrets, not Git.

## Proposed first deployment sequence

1. Commit a `CORS_ORIGINS` settings change and add tests for parsing/configuration.
2. Add a small backend container/build configuration for Cloud Run and test it locally; bind to the platform-provided `PORT`.
3. Create Supabase project; enable `vector`; run the schema migrations and verify the vector type/search path.
4. Create/import the reviewed demo dataset without putting a dump in Git; check row counts, embedding coverage, source URLs and statuses.
5. Deploy FastAPI to Cloud Run with `min-instances=0`, a strict max-instance value, an adequate memory limit, environment secrets and health check `/health`.
6. Deploy the frontend to Cloudflare Pages with `VITE_API_BASE_URL` pointing to the Cloud Run service. Add the exact Pages origin to `CORS_ORIGINS` and redeploy the API.
7. Verify `/health`, `/docs`, regulatory update fetch, English/Hindi/Marathi UI, RAG historical and unsupported-current-applicability queries, assessment submission/progress persistence, and browser console/network errors.
8. Publish the live link only after those browser/API checks pass. Record cold starts, the limits of free tier, and the no-auth prototype warning.

This is a provider assessment and deployment plan, not evidence that any hosted service exists. No live URL has been verified yet.
