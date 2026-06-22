from functools import lru_cache

import config
from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=1)
def get_embedding_model():
    """Load the embedding model once per process."""
    return SentenceTransformer(config.EMBEDDING_MODEL)


def embed_transactions(df):
    """Add sentence and embedding columns used by semantic retrieval."""
    if df.empty:
        df["sentence"] = []
        df["embedding"] = []
        return df

    df['sentence'] = df.apply(
        lambda row: f"spent ₹{row['Amount']} on {row['Merchant']} {row['Category']} on {row['Date']}",
        axis=1
    )
    df['embedding'] = get_embedding_model().encode(df['sentence'].tolist()).tolist()
    return df
