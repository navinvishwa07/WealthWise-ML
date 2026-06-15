from sentence_transformers import SentenceTransformer
import pandas as pd

model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_transactions(df):
    df['sentence'] = df.apply(
        lambda row: f"spent ₹{row['Amount']} on {row['Merchant']} {row['Category']} on {row['Date']}",
        axis=1
    )
    df['embedding'] = model.encode(df['sentence'].tolist()).tolist()
    return df