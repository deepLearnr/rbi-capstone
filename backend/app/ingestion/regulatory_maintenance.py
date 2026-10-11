"""Safe source-metadata and historical-summary maintenance helpers."""
from __future__ import annotations

from urllib.parse import urlparse


def validate_official_rbi_url(value: str) -> str:
    """Accept only HTTPS URLs on RBI's official domain or its subdomains."""
    url = (value or "").strip()
    parsed = urlparse(url)
    hostname = (parsed.hostname or "").lower().rstrip(".")
    if (
        parsed.scheme != "https"
        or not hostname
        or not (hostname == "rbi.org.in" or hostname.endswith(".rbi.org.in"))
        or not parsed.path.startswith("/")
    ):
        raise ValueError("Source URL must be an HTTPS URL on the official rbi.org.in domain.")
    return url


def historicalize_crr_simplification(simplification: dict) -> tuple[dict, bool]:
    """Change known CRR circular future-tense wording without altering figures/dates."""
    result = dict(simplification or {})
    replacements = {
        "The RBI has decided to reduce the Cash Reserve Ratio (CRR) for all banks by 100 basis points, bringing it down to 3.0 per cent of net demand and time Liabilities (NDTL). This reduction will be implemented in four equal tranches of 25 basis points each.":
        "The circular stated that the RBI would reduce the Cash Reserve Ratio (CRR) for all banks by 100 basis points, bringing it down to 3.0 per cent of net demand and time Liabilities (NDTL). It specified four equal tranches of 25 basis points each.",
        "The average Cash Reserve Ratio (CRR) required to be maintained by every bank is being reduced in four stages: to 3.75 per cent, 3.5 per cent, 3.25 per cent, and finally to 3.0 per cent of their NDTL.":
        "The circular specified a four-stage reduction in the average Cash Reserve Ratio (CRR) required to be maintained by every bank: to 3.75 per cent, 3.5 per cent, 3.25 per cent, and finally to 3.0 per cent of their NDTL.",
        "Banks are required to maintain the CRR at 3.75 per cent, 3.5 per cent, 3.25 per cent and 3.0 per cent of their NDTL effective from the reporting fortnight beginning September 6, October 4, November 1 and November 29, 2025, respectively.":
        "The circular specified CRR levels of 3.75 per cent, 3.5 per cent, 3.25 per cent and 3.0 per cent of NDTL for reporting fortnights beginning September 6, October 4, November 1 and November 29, 2025, respectively.",
    }
    changed = False
    for key in ("executive_summary", "what_changed"):
        value = result.get(key)
        if not isinstance(value, str):
            continue
        # Preserve the historical-source note separately from the original summary.
        if key == "executive_summary" and "\n\n" in value:
            prefix, body = value.split("\n\n", 1)
            updated = replacements.get(body, body)
            result[key] = prefix + "\n\n" + updated
        else:
            updated = replacements.get(value, value)
            result[key] = updated
        changed |= result[key] != value
    actions = result.get("what_should_i_do")
    if isinstance(actions, list):
        updated_actions = [replacements.get(item, item) if isinstance(item, str) else item for item in actions]
        changed |= updated_actions != actions
        result["what_should_i_do"] = updated_actions
    return result, changed
