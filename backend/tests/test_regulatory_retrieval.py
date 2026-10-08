from app.retrieval.service import retrieve_chunks


queries = [
    "What changed for Foreign Portfolio Investors under the 2026 KYC amendment?",
    "What is the new certified copy facility for Foreign Portfolio Investors?",
    "What does paragraph 5(1)(v) say about Foreign Portfolio Investors?",
]

for query in queries:
    print("\n" + "=" * 80)
    print(query)
    print("=" * 80)

    results = retrieve_chunks(query, top_k=5)

    for index, result in enumerate(results, start=1):
        print(
            f"#{index} "
            f"chunk_id={result.chunk.id} "
            f"distance={result.distance:.4f} "
            f"section={result.heading!r}"
        )
