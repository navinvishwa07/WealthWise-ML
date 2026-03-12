import pandas as pd
import random
import re
import numpy as np
from rapidfuzz import fuzz

HEADER_SYNONYMS = {
    "Description": [
        "Description",
        "Narration",
        "Transaction Remarks",
        "Remarks",
        "Details",
        "Particulars"
    ],
    
    "Date": [
        "Date",
        "Txn Date",
        "Transaction Date",
        "Value Date",
        "Posting Date"
    ],
    
    "Amount": [
        "Amount",
        "Withdrawal Amt",
        "Debit",
        "Dr Amount",
        "Transaction Amount",
        "Withdrawal Amt (INR)"
    ]
}

def sniff_headers(df):
    """
    Attempts to map the columns of the dataframe to the expected headers 
    (Description, Date, Amount) using a combination of exact matches and fuzzy matching.
    """
    
    column_mapping = {}

    for expected_header, synonyms in HEADER_SYNONYMS.items():
        for synonym in synonyms:
            for col in df.columns:
                if synonym.lower() == col.lower():
                    column_mapping[expected_header] = col
                    break
            if expected_header in column_mapping:
                break
    
    # If any expected header is missing, try fuzzy matching
    for expected_header in HEADER_SYNONYMS.keys():
        if expected_header not in column_mapping:
            best_match = None
            best_score = 0
            for col in df.columns:
                score = fuzz.ratio(expected_header.lower(), col.lower())
                if score > best_score:
                    best_score = score
                    best_match = col
            if best_score > 80:  # Threshold for accepting a match
                column_mapping[expected_header] = best_match
    
    return column_mapping

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
    
    
    reimbursement_pair = pd.DataFrame({
    "Date": [pd.Timestamp("2026-02-05"), pd.Timestamp("2026-02-07")],
    "Description": ["RAHUL-SHARMA-UPI", "RAHUL-SHARMA-UPI"],
    "Amount": [514, -514]
    })
    return pd.concat([pd.DataFrame(data), reimbursement_pair], ignore_index=True)

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
    column_mapping = sniff_headers(df)
    df = df.rename(columns={v: k for k, v in column_mapping.items()})
    df = df.dropna(subset=["Description", "Date", "Amount"])
    df["Amount"] = df["Amount"].apply(clean_amount)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df['Merchant'] = df['Description'].apply(clean_description)
    df['is_transfer'] = df['Description'].str.contains(r'TRANSFER|SELF|SAVINGS', case=False, na=False)
    df['is_investment'] = df['Description'].str.contains(r'SIP|NIFTY|INDEX|UTI|NIPPON', case=False, na=False)
    df = find_reimbursements(df)
    return df

def find_reimbursements(df):
    df["is_reimbursement"] = False
    matched = set()

    for i in range(len(df)):
        if i in matched:
            continue

        for j in range(len(df)):
            if j in matched or i == j:
                continue

            # Condition 1: time window
            days_apart = abs((df.loc[j, "Date"] - df.loc[i, "Date"]).days)

            # Condition 2: amount tolerance
            amount_match = abs(abs(df.loc[i, "Amount"]) - abs(df.loc[j, "Amount"])) <= 1

            # Condition 3: one debit (+ve), one credit (-ve)
            opposite_signs = (df.loc[i, "Amount"] > 0 and df.loc[j, "Amount"] < 0) or (df.loc[i, "Amount"] < 0 and df.loc[j, "Amount"] > 0)
            
            if days_apart <= 3 and amount_match and opposite_signs:
                df.loc[i, "is_reimbursement"] = True
                df.loc[j, "is_reimbursement"] = True
                matched.add(i)
                matched.add(j)
                break

    return df

def clean_amount(value):
    cleaned = re.sub(r'[₹,\s]', '', str(value))
    try:
        return float(cleaned)
    except ValueError:
        return 0.0
    

if __name__ == "__main__":
    raw_df = generate_mock_data()
    clean_df = process_data(raw_df)
    print("--- WealthWise Processed Data ---")
    print(clean_df[['Description', 'Merchant', 'is_transfer']].head(10))
