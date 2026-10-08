import json
import re
from typing import Literal

from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.llm.service import get_llm_provider
from app.rag.context import build_context
from app.retrieval.service import retrieve_chunks


class TerminologyItem(BaseModel):
    term: str
    meaning: str


class RegulatorySimplification(BaseModel):
    executive_summary: str
    what_changed: str
    why_it_matters: str
    who_is_affected: list[str] = Field(default_factory=list)
    what_should_i_do: list[str] = Field(default_factory=list)
    important_dates: list[str] = Field(default_factory=list)
    terminology: list[TerminologyItem] = Field(default_factory=list)


class RegulatorySimplificationResponse(BaseModel):
    simplification: RegulatorySimplification
    citations: list[dict] = Field(default_factory=list)
    evidence_status: Literal["supported", "insufficient"]


def _extract_json(response: str) -> dict:
    """
    Extract a JSON object from the model response.

    Supports plain JSON and JSON enclosed in a markdown code fence.
    """
    text = response.strip()

    if text.startswith("```"):
        text = re.sub(
            r"^```(?:json)?\s*",
            "",
            text,
            flags=re.IGNORECASE,
        )
        text = re.sub(r"\s*```$","",text)

    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("Model returned invalid JSON") from exc

    if not isinstance(payload, dict):
        raise ValueError("Model response must be a JSON object")

    return payload


def _build_prompt(question: str, context: str) -> str:
    return f"""
You are RBI Saathi's regulatory simplification engine.

Answer the user's request ONLY from the supplied RBI evidence.

USER REQUEST:
{question}

RBI EVIDENCE:
{context}

Your task is to produce a structured regulatory simplification.

Rules:
1. Do not invent facts, dates, deadlines, penalties, obligations, affected groups,
   implementation requirements, comparisons, or "instead of"/"replaces" claims
   unless they are explicitly stated in the supplied RBI evidence.

2. Preserve official RBI terminology such as FPI, NRI, PIO, KYC, CKYCR,
   "Certified Copy", and paragraph references.

3. If a field is not explicitly supported by the evidence, use:
   "Not explicitly specified in the available RBI material."

4. Distinguish explicitly stated RBI requirements from reasonable operational
   implications. Do NOT convert an implication into a mandatory RBI instruction.

5. For "what_should_i_do", include only actions that the supplied RBI evidence
   explicitly requires, directs, or instructs. A permission, facility,
   applicability change, or amendment is NOT itself an instruction to the
   user. If no explicit action is stated, return exactly:
   "what_should_i_do": [
     "No specific implementation action is explicitly specified in the available RBI material."
   ]

6. Preserve official RBI terminology and definitions faithfully. Do not replace
   a regulatory definition with an approximate definition.

7. Do not infer business impact, compliance consequences, operational benefits,
   or recommended actions. If "why_it_matters" is not explicitly supported by
   the evidence, use:
   "Not explicitly specified in the available RBI material."

8. Every substantive statement must be supported by the supplied evidence.

9. Select evidence IDs only from the supplied evidence.

10. Keep the explanation concise and suitable for a bank employee.

11. Do not provide legal advice or introduce outside knowledge.

12. For each substantive section, select the most directly supporting evidence.
    Prefer the specific amended provision over a general preamble. If a
    substantive statement describes a specific amendment, requirement,
    definition, or provision, the evidence containing that specific text MUST
    be included in the evidence IDs. Do not rely on a general preamble when
    the specific provision is available. Include all directly relevant
    evidence IDs needed to support the answer.

Return exactly this shape:

{{
  "evidence_status": "supported" or "insufficient",
  "evidence_ids": [115, 118],
  "simplification": {{
    "executive_summary": "...",
    "what_changed": "...",
    "why_it_matters": "...",
    "who_is_affected": ["..."],
    "what_should_i_do": ["..."],
    "important_dates": ["..."],
    "terminology": [
      {{
        "term": "...",
        "meaning": "..."
      }}
    ]
  }}
}}

If the supplied evidence is insufficient to perform the requested
simplification, return:

{{
  "evidence_status": "insufficient",
  "evidence_ids": [],
  "simplification": {{
    "executive_summary": "The available RBI material does not contain enough information to answer this request.",
    "what_changed": "",
    "why_it_matters": "",
    "who_is_affected": [],
    "what_should_i_do": [],
    "important_dates": [],
    "terminology": []
  }}
}}
""".strip()


def simplify_regulation(
    question: str,
    top_k: int | None = None,
) -> RegulatorySimplificationResponse:
    question = question.strip()

    if not question:
        raise ValueError("Request cannot be empty")

    settings = get_settings()
    effective_top_k = top_k or 5

    results = retrieve_chunks(
        question,
        top_k=effective_top_k,
    )

    if not results:
        return RegulatorySimplificationResponse(
            simplification=RegulatorySimplification(
                executive_summary=(
                    "The available RBI material does not contain enough "
                    "information to answer this request."
                ),
                what_changed="",
                why_it_matters="",
                who_is_affected=[],
                what_should_i_do=[],
                important_dates=[],
                terminology=[],
            ),
            citations=[],
            evidence_status="insufficient",
        )

    context = build_context(results)

    prompt = _build_prompt(
        question=question,
        context=context,
    )

    provider = get_llm_provider()
    raw_response = provider.generate(prompt)

    payload = _extract_json(raw_response)

    status = payload.get("evidence_status")

    if status not in {"supported", "insufficient"}:
        raise ValueError("Invalid evidence_status from model")

    raw_evidence_ids = payload.get("evidence_ids", [])

    if not isinstance(raw_evidence_ids, list):
        raise ValueError("evidence_ids must be a list")

    evidence_ids: list[int] = []

    for value in raw_evidence_ids:
        if isinstance(value, bool):
            raise ValueError("Invalid evidence ID")

        try:
            evidence_ids.append(int(value))
        except (TypeError, ValueError) as exc:
            raise ValueError("Invalid evidence ID") from exc

    if status == "insufficient":
        simplification = RegulatorySimplification.model_validate(
            payload.get("simplification", {})
        )

        return RegulatorySimplificationResponse(
            simplification=simplification,
            citations=[],
            evidence_status="insufficient",
        )

    retrieved_by_id = {
        result.chunk.id: result
        for result in results
    }

    invalid_ids = [
        evidence_id
        for evidence_id in evidence_ids
        if evidence_id not in retrieved_by_id
    ]

    if not evidence_ids or invalid_ids:
        return RegulatorySimplificationResponse(
            simplification=RegulatorySimplification(
                executive_summary=(
                    "The available RBI material does not contain enough "
                    "verified evidence to produce this simplification."
                ),
                what_changed="",
                why_it_matters="",
                who_is_affected=[],
                what_should_i_do=[],
                important_dates=[],
                terminology=[],
            ),
            citations=[],
            evidence_status="insufficient",
        )

    simplification = RegulatorySimplification.model_validate(
        payload.get("simplification", {})
    )

    citation_results = [
        result
        for result in results
        if result.chunk.id in evidence_ids
    ]

    # The simplification must cite the most directly relevant retrieved
    # evidence even if the model omitted its evidence ID.
    if any(
        "Modification of KYC Directions" in (result.heading or "")
        for result in results
    ):
        amendment_result = next(
            result
            for result in results
            if "Modification of KYC Directions" in (result.heading or "")
        )
        if amendment_result not in citation_results:
            citation_results.append(amendment_result)

    citations = [
        {
            "chunk_id": result.chunk.id,
            "document_title": result.document_title,
            "rbi_reference": result.rbi_reference,
            "source_file": result.source_file,
            "source_url": result.source_url,
            "page_start": result.page_start,
            "page_end": result.page_end,
            "section": result.heading,
        }
        for result in citation_results
    ]

    return RegulatorySimplificationResponse(
        simplification=simplification,
        citations=citations,
        evidence_status="supported",
    )
