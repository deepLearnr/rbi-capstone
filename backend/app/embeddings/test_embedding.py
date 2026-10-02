from app.embeddings.service import embed_passages, embed_query


texts = [
    "RBI KYC requirements for regulated entities.",
    "Customer identification and verification procedures."
]

passage_embeddings = embed_passages(texts)
query_embedding = embed_query("What are the KYC requirements?")

print("Passage count:", len(passage_embeddings))
print("Passage dimensions:", len(passage_embeddings[0]))
print("Query dimensions:", len(query_embedding))
print("First 5 values:", passage_embeddings[0][:5])
