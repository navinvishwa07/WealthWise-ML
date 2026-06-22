from embedding import get_embedding_model
from vector_store import collection


def semantic_search(query, n_results=5):
    """Return semantically similar transaction documents for a search query."""
    if collection.count() == 0:
        return {"documents": [[]], "distances": [[]]}

    query_embedding = get_embedding_model().encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=min(n_results, collection.count())
    )
    return results
