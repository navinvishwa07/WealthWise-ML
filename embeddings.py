from sentence_transformers import SentenceTransformer
import pandas as pd

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def embed_transactions(df):
    # Create text using the required template
    df['combined'] = df.apply(
        lambda row: f"spent ₹{row['Amount']} on {row['Merchant']} "
                    f"{row['Category']} on {row['Date']}",
        axis=1
    )
    
    # Generate embeddings
    embeddings = model.encode(df['combined'].tolist())
    
    return embeddings