# Regulatory metadata maintenance

The maintenance command is read-only by default:

```bash
cd backend
source .venv-rbi/bin/activate
python -m scripts.maintain_regulatory_updates
```

It reports regulatory updates with missing official source URLs and detects the known
future-tense phrasing in the CRR circular summary. It does not invent URLs.

The official RBI notification for `RBI/2026-27/257` has been verified against its
reference and title. Its URL is:

`https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=13699&Mode=0`

Pass that exact URL explicitly when repairing an existing database record. The URL
validator accepts HTTPS URLs only on `rbi.org.in` or an official subdomain:

```bash
python -m scripts.maintain_regulatory_updates --kyc-source-url 'https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=13699&Mode=0'
```

That remains a dry run. Add `--write` only after reviewing the proposed changes:

```bash
python -m scripts.maintain_regulatory_updates --kyc-source-url 'https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=13699&Mode=0' --write
```

The script also updates the known historical wording of `RBI/2025-26/46` without
changing the CRR figures or dates. It modifies existing records only; it never
creates regulatory updates. If the official page cannot be independently confirmed
in a future maintenance run, do not substitute a guessed URL.


## Canonical ingestion metadata

The document ingestion paths also preserve verified provenance when these files are
ingested into a fresh database:

- `RBI_KYC.pdf`: FAQ publication date `2025-06-09` and the official RBI FAQ URL.
- `KYC_Rule_Commercial.pdf`: the official notification URL for `RBI/2026-27/257`.
- `ucb_cyber_security_framework.pdf`: the official notification URL for
  `RBI/2019-20/129`; its source profile continues to mark the supplied PDF as
  `withdrawn` historical material.

A source URL records provenance; it does not by itself establish current regulatory
applicability. The FAQ and KYC amendment ingestion paths deliberately do not mark
those records active without separately verified status evidence.
