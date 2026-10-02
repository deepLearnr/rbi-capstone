from app.rag.prompt import build_rag_prompt
from app.retrieval.service import retrieve_chunks


question = "What is a KYC Identifier and when can it be used?"

results = retrieve_chunks(question, top_k=3)

prompt = build_rag_prompt(
    question=question,
    results=results,
)

print(prompt)
