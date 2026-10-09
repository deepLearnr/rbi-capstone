import re
from typing import Literal

from app.core.config import get_settings
from app.llm.service import get_llm_provider
from app.rag.prompt import build_rag_prompt
from app.rag.schemas import RAGAnswer, SourceCitation
from app.retrieval.service import retrieve_chunks

CURRENT_APPLICABILITY_PATTERN = re.compile(
    r"\b("
    r"currently|current|today|presently|latest|"
    r"still in force|in force|remains applicable|"
    r"currently applicable|current requirements|"
    r"as of now|now applicable"
    r")\b",
    flags=re.IGNORECASE,
)


def asks_about_current_applicability(question: str) -> bool:
    return bool(CURRENT_APPLICABILITY_PATTERN.search(question))

def parse_evidence_response(response: str) -> tuple[
    Literal["supported", "insufficient"],
    list[int],
    str,
]:
    lines = response.strip().splitlines()

    status: Literal["supported", "insufficient"] | None = None
    evidence_ids: list[int] = []
    answer_lines: list[str] = []
    in_answer = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("EVIDENCE_STATUS:"):
            raw_status = stripped[len("EVIDENCE_STATUS:"):].strip().lower()
            if raw_status in ("supported", "insufficient"):
                status = raw_status
            continue

        if stripped.startswith("EVIDENCE_IDS:"):
            raw_ids = stripped[len("EVIDENCE_IDS:"):].strip()
            if raw_ids:
                matches = re.findall(r"\b\d+\b", raw_ids)
                evidence_ids = [int(m) for m in matches]
            continue

        if stripped.startswith("ANSWER:"):
            in_answer = True
            first_line = stripped[len("ANSWER:"):].strip()
            if first_line:
                answer_lines.append(first_line)
            continue

        if in_answer:
            answer_lines.append(line)

    answer = "\n".join(answer_lines).strip()

    # Fail closed if status is missing or invalid
    if status is None:
        return (
            "insufficient",
            [],
            "The available RBI material does not contain enough "
            "information to answer this question.",
        )

    if not answer:
        return (
            "insufficient",
            [],
            "The available RBI material does not contain enough "
            "information to answer this question.",
        )

    if status == "insufficient":
        return "insufficient", [], answer

    # Supported status MUST have valid supporting evidence IDs
    if not evidence_ids:
        return (
            "insufficient",
            [],
            "The available RBI material does not contain enough "
            "information to answer this question.",
        )

    return "supported", evidence_ids, answer


def answer_question(
    question: str,
    top_k: int | None = None,
) -> RAGAnswer:
    question = question.strip()

    if not question:
        raise ValueError("Question cannot be empty")

    settings = get_settings()
    effective_top_k = top_k or settings.retrieval_top_k

    results = retrieve_chunks(
        question,
        top_k=effective_top_k,
    )

    if not results:
        return RAGAnswer(
            answer=(
                "The available RBI material does not contain enough "
                "information to answer this question."
            ),
            citations=[],
            evidence_status="insufficient",
        )

    prompt = build_rag_prompt(
        question=question,
        results=results,
    )

    provider = get_llm_provider()
    raw_response = provider.generate(prompt)

    evidence_status, evidence_ids, answer = parse_evidence_response(raw_response)

    if evidence_status == "insufficient":
        return RAGAnswer(
            answer=answer,
            citations=[],
            evidence_status="insufficient",
        )

    # Validate returned evidence IDs against retrieved chunks
    retrieved_by_id = {result.chunk.id: result for result in results}
    invalid_ids = [eid for eid in evidence_ids if eid not in retrieved_by_id]

    if invalid_ids:
        # Fail closed if model hallucinated an unretrieved chunk ID
        return RAGAnswer(
            answer=(
                "The available RBI material does not contain enough "
                "information to answer this question."
            ),
            citations=[],
            evidence_status="insufficient",
        )

    citations = [
        SourceCitation(
            chunk_id=retrieved_by_id[eid].chunk.id,
            document_title=retrieved_by_id[eid].document_title,
            rbi_reference=retrieved_by_id[eid].rbi_reference,
            source_file=retrieved_by_id[eid].source_file,
            source_url=retrieved_by_id[eid].source_url,
            page_start=retrieved_by_id[eid].page_start,
            page_end=retrieved_by_id[eid].page_end,
            section=retrieved_by_id[eid].heading,
            regulatory_status=retrieved_by_id[eid].regulatory_status,
        )
        for eid in evidence_ids
    ]

    withdrawn_citations = [
        citation
        for citation in citations
        if (citation.regulatory_status or "").strip().lower()
        == "withdrawn"
    ]

    has_withdrawn_citation = bool(withdrawn_citations)
    has_non_withdrawn_citation = any(
        (citation.regulatory_status or "").strip().lower() != "withdrawn"
        for citation in citations
    )

    if (
        asks_about_current_applicability(question)
        and has_withdrawn_citation
        and not has_non_withdrawn_citation
    ):
        return RAGAnswer(
            answer=(
                "The retrieved evidence includes a document marked "
                "withdrawn and does not establish current regulatory "
                "applicability. Please consult the applicable current "
                "RBI directions before relying on these requirements."
            ),
            citations=[],
            evidence_status="insufficient",
        )

    if withdrawn_citations and not re.search(
        r"\bwithdrawn\b",
        answer,
        flags=re.IGNORECASE,
    ):
        answer = (
            "Historical-source warning: This answer cites an RBI "
            "document marked withdrawn in the source metadata. "
            "It is historical material and does not establish "
            "current regulatory requirements.\n\n"
            + answer
        )

    return RAGAnswer(
        answer=answer,
        citations=citations,
        evidence_status="supported",
    )