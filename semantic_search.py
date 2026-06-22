from embedding import get_embedding
from vector_store import collection


def semantic_search(query, n_results=5):
    # Convert the user's search into an embedding
    query_embedding = get_embedding(query)

    # Search the vector database
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    # Return the results
    return results