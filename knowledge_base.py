import chromadb
from pypdf import PdfReader

import config
from embedding import get_embedding_model

client = chromadb.PersistentClient(path=config.VECTOR_DB_PATH)
kb_collection = client.get_or_create_collection(name=config.KNOWLEDGE_COLLECTION)


def chunk_text(text, chunk_size=500, overlap=50):
    """Splits text into overlapping chunks for embedding."""
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be greater than overlap")

    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks


def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += (page.extract_text() or "") + "\n"
    return text


def load_document(file, filename):
    """Accepts an uploaded PDF, chunks it, embeds it, stores it."""
    text = extract_text_from_pdf(file)
    chunks = chunk_text(text)

    if not chunks:
        return 0

    embeddings = get_embedding_model().encode(chunks).tolist()
    kb_collection.upsert(
        ids=[f"{filename}_{i}" for i in range(len(chunks))],
        embeddings=embeddings,
        documents=chunks,
        metadatas=[{"source": filename} for _ in chunks]
    )
    return len(chunks)


def query_knowledge_base(query_text, n_results=3):
    if kb_collection.count() == 0:
        return {"documents": [[]]}
    
    query_vector = get_embedding_model().encode([query_text]).tolist()
    results = kb_collection.query(
        query_embeddings=query_vector,
        n_results=min(n_results, kb_collection.count())
    )
    return results
