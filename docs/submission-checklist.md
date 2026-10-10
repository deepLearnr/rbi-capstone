# Submission checklist

Mark each item only after checking it in the checkout being submitted.

## Reproducibility
- [ ] `README.md` setup instructions match the current branch and environment.
- [ ] `backend/requirements.txt` installs the dependencies in a clean environment.
- [ ] `.env` is local only; no keys/passwords or database dumps are committed.
- [ ] Database migrations complete on a fresh database with pgvector enabled.
- [ ] Demo seed script completes and is safe to rerun.

## Automated checks
- [ ] `python -m pytest -q` passes; record the actual count and command.
- [ ] `npm run build` succeeds.
- [ ] `npm run lint` succeeds, or any remaining warnings are documented.
- [ ] `/health` returns HTTP 200.
- [ ] `/docs` loads and shows the expected routes.

## End-to-end demo
- [ ] A source document is present in the database with source URL and metadata.
- [ ] Its chunks exist and have 384-dimensional embeddings.
- [ ] A question grounded in that source returns citations.
- [ ] An unsupported question does not receive a fabricated supported answer.
- [ ] Learning module/assessment/progress flow works with the actual demo data.
- [ ] The UI is tested in the browser at the presentation viewport size.

## Submission hygiene
- [ ] `git status` reviewed; only intended files are included.
- [ ] No `.env`, credentials, tokens, virtual environments, `node_modules`, caches, or database dumps.
- [ ] README distinguishes implemented features from prototype/mock views.
- [ ] Demo uses official source content and does not claim unverified legal applicability.
- [ ] Final archive/repository opens on another machine using the README.

## Known limitations to disclose
- This is a prototype, not legal advice or production compliance software.
- RBI source discovery/extraction must be reviewed; current legal status is not inferred.
- The circulars endpoint currently uses in-memory storage.
- Some frontend routes may be UI-first rather than connected to persistent backend APIs.
- Live LLM functionality depends on Ollama/OpenRouter configuration.
