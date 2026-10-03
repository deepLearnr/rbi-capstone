from typing import Literal

from app.core.config import get_settings
from app.llm.service import get_llm_provider
from app.rag.prompt import build_rag_prompt
from app.rag.schemas import RAGAnswer, SourceCitation
from app.retrieval.service import retrieve_chunks


def parse_evidence_response(response: str) -> tuple[
    Literal["supported", "insufficient"],
    str,
]:
    response = response.strip()

    supported_marker = "EVIDENCE_STATUS: supported"
    insufficient_marker = "EVIDENCE_STATUS: insufficient"

    if response.startswith(supported_marker):
        status = "supported"
    elif response.startswith(insufficient_marker):
        status = "insufficient"
    else:
        # Fail closed if the model does not follow the required format.
        return (
            "insufficient",
            "The available RBI material does not contain enough "
            "information to answer this question.",
        )

    answer = response[len(
        supported_marker
        if status == "supported"
        else insufficient_marker
    ):].strip()

    if answer.startswith("ANSWER:"):
        answer = answer[len("ANSWER:"):].strip()

    if not answer:
        return (
            "insufficient",
            "The available RBI material does not contain enough "
            "information to answer this question.",
        )

    return status, answer


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

    evidence_status, answer = parse_evidence_response(raw_response)

    citations = [
        SourceCitation(
            chunk_id=result.chunk.id,
            document_title=result.document_title,
            rbi_reference=result.rbi_reference,
            source_file=result.source_file,
            source_url=result.source_url,
            page_start=result.page_start,
            page_end=result.page_end,
            section=result.heading,
        )
        for result in results
    ]

    return RAGAnswer(
        answer=answer,
        citations=citations,
        evidence_status=evidence_status,
    )
