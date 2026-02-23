import json
import os
from rapidfuzz import fuzz

# Name of the file where merchant-category mappings are stored
RULES_FILE = "user_rules.json"


def load_rules():
    """
    Loads merchant-category mappings from the JSON file.
    Returns a dictionary.
    If the file does not exist or is invalid, returns an empty dictionary.
    """
    # Check if the rules file exists
    if not os.path.exists(RULES_FILE):
        return {}

    # Open and attempt to load JSON content
    with open(RULES_FILE, "r") as file:
        try:
            return json.load(file)  # Convert JSON to Python dictionary
        except json.JSONDecodeError:
            return {}  # Return empty dictionary if file is corrupted


def save_rules(merchant, category):
    """
    Saves or updates a merchant-category pair in the JSON file.
    """
    # Load existing rules into a dictionary
    rules = load_rules()

    # Add or update the merchant with its category
    rules[merchant] = category

    # Write updated rules back to the JSON file
    with open(RULES_FILE, "w") as file:
        json.dump(rules, file, indent=4)


def cluster_merchant(df, threshold=90):
    """
    Groups similar merchant names using fuzzy matching.
    Returns a list of clusters.
    """
    # Get unique merchant names from dataframe
    unique_merchants = df["merchant"].unique()

    clusters = []      # Stores final grouped clusters
    visited = set()    # Tracks merchants already grouped

    # Loop through each merchant
    for merchant in unique_merchants:
        if merchant in visited:
            continue  # Skip if already grouped

        cluster = [merchant]  # Start a new cluster
        visited.add(merchant)

        # Compare with other merchants
        for other in unique_merchants:
            if other in visited:
                continue

            # Calculate similarity score (0–100)
            score = fuzz.token_sort_ratio(str(merchant), str(other))

            # If similarity above threshold, group together
            if score >= threshold:
                cluster.append(other)
                visited.add(other)

        clusters.append(cluster)  # Save completed cluster

    return clusters


def get_category(merchant, rules, threshold=90):
    """
    Determines category using:
    1. Exact match
    2. Fuzzy match
    3. Default fallback
    """

    # 1. Exact match check (fastest and most accurate)
    if merchant in rules:
        return rules[merchant]

    # 2. Fuzzy match against known merchants in rules
    best_match = None
    highest_score = 0

    for known_merchant in rules.keys():
        score = fuzz.token_sort_ratio(str(merchant), str(known_merchant))

        if score > highest_score:
            highest_score = score
            best_match = known_merchant

    # If best match is strong enough, use its category
    if highest_score >= threshold:
        return rules[best_match]

    # 3. If no match found, return default
    return "UNCATEGORIZED"


def apply_classification(df):
    """
    Applies category classification to a dataframe.
    Adds a new 'Category' column.
    """
    # Load stored merchant-category rules
    rules = load_rules()

    # Apply classification to each merchant in dataframe
    df['Category'] = df['Merchant'].apply(
        lambda x: get_category(x, rules)
    )

    return df