# RBI circular discovery and ingestion

The RBI discovery/ingestion workflow is designed to fail closed. It does not infer legal applicability, withdrawal, supersession, effective dates, or simplifications from a title alone.

## 1. Dry-run first

From the backend directory:

```bash
source .venv-rbi/bin/activate
python -m app.ingestion.ingest_discovered_rbi \
  --index-url 'https://www.rbi.org.in/Scripts/BS_CircularIndexDisplay.aspx?Id=12858'
```

The command defaults to dry-run and should not mutate the database. For this example, the verified metadata is:

- Title: `Maintenance of Cash Reserve Ratio (CRR)`
- Reference: `RBI/2025-26/46`
- Publication date: `2025-06-06`
- Content type: official RBI HTML (the page may not link a separate PDF)

The HTML extractor removes scripts and common navigation/footer text, verifies title/reference/date, and separates the main circular from its attached `NOTIFICATION` into distinct chunks. It should reject content that is too short or cannot be verified.

## 2. Real ingestion (only after reviewing the dry-run)

```bash
python -m app.ingestion.ingest_discovered_rbi \
  --index-url 'https://www.rbi.org.in/Scripts/BS_CircularIndexDisplay.aspx?Id=12858' \
  --write
```

The write path validates metadata and official HTTPS URLs, downloads only eligible direct PDF resources, verifies PDF signatures and size limits, or extracts verified HTML text. It checks duplicates, computes embeddings for the new chunks, and writes the document and chunks in one transaction. The CLI does not automatically create a `RegulatoryUpdate` or invent simplification content.

After a successful write, verify the reported document ID and chunk count in the database and test retrieval through `/api/assistant/query`. A dry-run is not evidence that a document was persisted or indexed.

## 3. Safety and limitations

- Only HTTPS URLs on the explicit RBI host allowlist are accepted.
- Redirects and content size are checked.
- A link label alone does not establish that the resource is a PDF.
- HTML pages are variable; inspect extracted content and chunk boundaries when adding a new page layout.
- Duplicate detection uses source URL, RBI reference, and source filename, but concurrent ingestion still requires care.
- An official RBI page does not establish whether a circular remains in force.
- If title, reference, date, or content cannot be verified, do not override the checks manually just to make ingestion succeed.

## 4. Report-only discovery

For candidate reports without database writes:

```bash
python -m app.ingestion.discover_rbi \
  --max-candidates 25 \
  --output ../data/rbi_discovery_report.json
```

If the landing page cannot expose candidate links, use a known official detail page with `--index-url`. The report is a discovery aid, not legal validation.
