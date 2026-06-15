import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="transactions")

def store_embeddings(df):
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

def query_similar(query_text, n_results=5):
    query_vector = model.encode([query_text]).tolist()
    results = collection.query(
        query_embeddings=query_vector,
        n_results=n_results
    )
    return results