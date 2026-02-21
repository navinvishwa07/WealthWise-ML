import pandas as pd
import random
import re

def generate_mock_data(rows=15):
    """
    Generates a mock financial dataset with messy UPI strings, 
    personal names, and investment patterns.
    """
    # Common merchant patterns for testing Regex and Fuzzy Matching
    descriptions = [
        "UPI/DDSTORE/20260220/1", "DDSTORE-PAYTM-99", "UPI/DD-STORE/CHNI", # Canteen
        "SWIGGY-ORDER-442", "ZOMATO-LUNCH-91",                           # Food
        "TRANSFER-TO-SAVINGS-ACC", "SELF-TRANSFER-HDFC",                # Internal
        "UTI-NIFTY-50-INDEX-SIP", "NIPPON-SMALL-CAP-SIP",               # Investments
        "RAHUL-SHARMA-UPI", "S-VISHAL-PAY",                             # Personal Names
        "AMAZON-IND-SHOP", "FLIPKART-ORDER"                             # Shopping
    ]
            
    data = {
        "Date": pd.date_range(start="2026-02-01", periods=rows, freq="D"),
        "Description": [random.choice(descriptions) for _ in range(rows)],
        "Amount": [random.randint(10, 2000) for _ in range(rows)]
    }
    
    return pd.DataFrame(data)

def clean_description(description):
    if pd.isna(description):
        return "UNKNOWN"
    
    # 1. Try to find name after UPI/
    match = re.search(r'UPI/([^/0-9-]+)', description, re.IGNORECASE)
    if match:
        return match.group(1).strip().upper()
    
    # 2. Fallback: Grab the first block of letters
    fallback = re.search(r'([A-Za-z]+)', description)
    return fallback.group(1).upper() if fallback else description.upper()

def process_data(df):
    """Pipeline to clean and flag the dataframe"""
    # Create the Merchant column
    df['Merchant'] = df['Description'].apply(clean_description)
    
    # Flag transfers (Important for your 2k SIP / 5k Income logic)
    df['is_transfer'] = df['Description'].str.contains(
        r'TRANSFER|SELF|SAVINGS', 
        case=False, 
        na=False
    )
    return df

if __name__ == "__main__":
    # Now we call them in order
    raw_df = generate_mock_data()
    clean_df = process_data(raw_df)
    
    print("--- WealthWise Processed Data ---")
    print(clean_df[['Description', 'Merchant', 'is_transfer']].head(10))