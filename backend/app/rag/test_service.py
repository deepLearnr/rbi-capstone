from app.rag.service import answer_question


question = "What is a KYC Identifier and when can it be used?"

result = answer_question(question, top_k=3)

print("\n" + "=" * 80)
print("ANSWER")
print("=" * 80)
print(result.answer)

print("\n" + "=" * 80)
print("GROUNDED")
print("=" * 80)
print(result.grounded)

print("\n" + "=" * 80)
print("CITATIONS")
print("=" * 80)

for citation in result.citations:
    print(
        f"- chunk={citation.chunk_id} "
        f"document={citation.document_title} "
        f"pages={citation.page_start}-{citation.page_end} "
        f"section={citation.section}"
    )
