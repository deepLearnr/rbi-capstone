from app.retrieval.service import retrieve_chunks


query = "What are the KYC requirements for customer identification?"

results = retrieve_chunks(query, top_k=5)

print(f"\nRetrieved {len(results)} chunks:\n")

for rank, result in enumerate(results, start=1):
    print("=" * 80)
    print(f"Rank: {rank}")
    print(f"Chunk ID: {result.chunk.id}")
    print(f"Heading: {result.heading}")
    print(f"Pages: {result.page_start}-{result.page_end}")
    print(f"Document: {result.document_title}")
    print(f"RBI reference: {result.rbi_reference}")
    print(f"Source file: {result.source_file}")
    print(f"Source URL: {result.source_url}")
    print(f"Distance: {result.distance:.6f}")
    print()
    print(result.chunk.content[:700])
    print()
