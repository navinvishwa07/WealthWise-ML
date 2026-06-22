import chromadb

import config
from embedding import get_embedding_model

client = chromadb.PersistentClient(path=config.VECTOR_DB_PATH)
collection = client.get_or_create_collection(name=config.TRANSACTION_COLLECTION)


def _clear_collection():
    existing = collection.get()
    if existing["ids"]:
        collection.delete(ids=existing["ids"])


def store_embeddings(df):
    """Persist the current transaction embeddings for RAG retrieval."""
    if df.empty:
        _clear_collection()
        return 0

    _clear_collection()
    collection.upsert(
        ids=[str(i) for i in df.index],
        embeddings=df['embedding'].tolist(),
        documents=df['sentence'].tolist(),
        metadatas=[
            {
                "merchant": row['Merchant'],
                "category": row['Category'],
                "amount": float(row['Amount']),
                "date": str(row['Date'])
            }
            for _, row in df.iterrows()
        ]
    )
    return len(df)


def query_similar(query_text, n_results=5):
    if collection.count() == 0:
        return {"documents": [[]]}

    query_vector = get_embedding_model().encode([query_text]).tolist()
    results = collection.query(
        query_embeddings=query_vector,
        n_results=min(n_results, collection.count())
    )
    return results
