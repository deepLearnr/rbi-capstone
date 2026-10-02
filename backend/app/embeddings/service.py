from functools import lru_cache

from sentence_transformers import SentenceTransformer


MODEL_NAME = "intfloat/multilingual-e5-small"


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


def embed_passages(texts: list[str]) -> list[list[float]]:
    model = get_embedding_model()

    inputs = [f"passage: {text}" for text in texts]

    embeddings = model.encode(
        inputs,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )

    return embeddings.tolist()


def embed_query(query: str) -> list[float]:
    model = get_embedding_model()

    embedding = model.encode(
        f"query: {query}",
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )

    return embedding.tolist()
