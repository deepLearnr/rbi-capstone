# RAG prompt, citations and guardrails

## Request contract

`POST /api/assistant/query` accepts:

```json
{
  "question": "What did this circular state?",
  "top_k": 3,
  "role": "bank_employee"
}
```

`question` is required (1–2,000 characters). `top_k` is 1–10, defaulting to 3. Supported roles are `bank_employee`, `compliance_officer`, `branch_manager`, and `customer_support`.

The response contains `answer`, `citations`, and `evidence_status` (`supported` or `insufficient`). Each citation is assembled by the server from a retrieved chunk and includes its chunk ID, document title, RBI reference, source file/URL, page range, section, and regulatory status when available.

## Prompt design

The prompt in `backend/app/rag/prompt.py` directs the LLM to:

- answer only from the supplied RBI context and not fill gaps using general knowledge;
- preserve source-supported dates, thresholds, terminology, conditions and exceptions;
- answer in the language of the question, translating explanatory language without changing regulatory meaning;
- return a strict `EVIDENCE_STATUS`, `EVIDENCE_IDS`, and `ANSWER` format;
- cite only the supplied evidence IDs and treat merely related chunks as insufficient;
- distinguish historical material from current applicability, treat `withdrawn` metadata as historical, and not infer supersession without explicit evidence.

Role guidance changes presentation only. It must not create obligations, exceptions or facts.

## Deterministic post-generation checks

`backend/app/rag/service.py` applies server-side controls after the provider responds:

1. The parser fails closed when the status, answer or required evidence IDs are missing/invalid.
2. Evidence IDs are checked against the actual retrieved chunk IDs. An invented ID returns an `insufficient` answer with no citations.
3. For a question that matches the current-applicability phrase detector, every returned citation must have `regulatory_status` equal to `active` (case-insensitive, after trim). A missing status or a withdrawn status is not proof that a rule is current; the service returns `insufficient` and no citations.
4. If a historical answer uses withdrawn evidence, a historical-source warning is prefixed unless the answer already mentions withdrawal.
5. Citation metadata is generated from the matched database chunk; the LLM does not supply its own document URLs or page metadata.

The current-applicability check is intentionally conservative. It is not an RBI legal-status registry and does not determine whether one circular supersedes another. Active status must come from separately verified metadata, not just a source URL.

## Source and freshness limitations

- The phrase detector is keyword-based and currently uses English expressions such as `current`, `today`, `latest`, and `still in force`. It will not reliably recognize every wording or every language.
- There is no automated legal supersession graph or scheduled official-source status verification.
- Official URLs establish provenance, not that a direction remains in force.
- A historical query can be supported by a historical source even when a current-applicability question must be refused.
- A source without a stored URL can still appear as file-based evidence; source traceability is weaker and should be repaired where the official destination is verified.

### Observed local status metadata (12 October 2026)

| Document | Chunk status observed | Implication |
|---|---|---|
| KYC FAQ dated 9 June 2025 | Unset on 37 chunks | Historical FAQ is traceable to its official page; not marked active. |
| Commercial-bank KYC amendment, `RBI/2026-27/257` | Unset on 4 chunks | Official source URL is stored; not marked active merely because the URL is official. |
| UCB cyber-security framework, `RBI/2019-20/129` | `withdrawn` on 47 chunks | Historical evidence only for current-applicability questions. |
| CRR circular, `RBI/2025-26/46` | Unset on 2 chunks | Historical circular does not by itself establish the present CRR requirement. |

This table records the observed local database snapshot; it is not a live regulatory-status assertion.

## Relevant tests

The backend test suite includes cases for empty retrieval, invalid/unretrieved evidence IDs, withdrawn-only support for current applicability, historical answers from withdrawn material, missing/unknown status for current-applicability questions, prompt construction, and discovery/simplification acceptance. Always record results from the actual checkout being submitted.
