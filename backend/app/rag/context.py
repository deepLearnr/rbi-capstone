from app.retrieval.service import RetrievedChunk


def build_context(results: list[RetrievedChunk]) -> str:
    sections = []

    for result in results:
        page_reference = str(result.page_start or "")

        if result.page_end and result.page_end != result.page_start:
            page_reference = (
                f"{result.page_start}-{result.page_end}"
            )

        sections.append(
            "\n".join(
                [
                    f"[EVIDENCE_ID: {result.chunk.id}]",
                    f"Document: {result.document_title}",
                    f"RBI Reference: {result.rbi_reference or 'Not available'}",
                    f"Pages: {page_reference or 'Not available'}",
                    f"Section: {result.heading or 'Not available'}",
                    f"Source File: {result.source_file or 'Not available'}",
                    "",
                    result.chunk.content,
                ]
            )
        )

    return "\n\n---\n\n".join(sections)