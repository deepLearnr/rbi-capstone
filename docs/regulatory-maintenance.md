# Regulatory metadata maintenance

The maintenance command is read-only by default:

```bash
cd backend
source .venv-rbi/bin/activate
python -m scripts.maintain_regulatory_updates
```

It reports regulatory updates with missing official source URLs and detects the known
future-tense phrasing in the CRR circular summary. It does not invent URLs.

After independently verifying the exact official RBI page for `RBI/2026-27/257`,
pass that URL explicitly to the command. The URL validator accepts HTTPS URLs only
on `rbi.org.in` or an official subdomain:

```bash
python -m scripts.maintain_regulatory_updates --kyc-source-url 'VERIFIED_OFFICIAL_RBI_URL'
```

That remains a dry run. Add `--write` only after reviewing the proposed changes:

```bash
python -m scripts.maintain_regulatory_updates --kyc-source-url 'VERIFIED_OFFICIAL_RBI_URL' --write
```

The script also updates the known historical wording of `RBI/2025-26/46` without
changing the CRR figures or dates. It modifies existing records only; it never
creates regulatory updates. If the KYC URL has not been verified, leave it unset.
