from app.core.config import get_settings
from app.llm.service import get_llm_provider
from app.rag.prompt import build_rag_prompt
from app.rag.schemas import RAGAnswer, SourceCitation
from app.retrieval.service import retrieve_chunks


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
            grounded=False,
        )


    prompt = build_rag_prompt(
        question=question,
        results=results,
    )

    provider = get_llm_provider()
    answer = provider.generate(prompt)

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
        grounded=True,
    )