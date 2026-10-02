from app.rag.context import build_context
from app.retrieval.service import retrieve_chunks


query = "What are the KYC requirements for customer identification?"

results = retrieve_chunks(query, top_k=3)

context = build_context(results)

print(context)
