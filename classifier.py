import json
import os
from rapidfuzz import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier

RULES_FILE = "user_rules.json"

def load_rules():
    """Loads merchant-category mappings from JSON. Returns empty dict if missing."""
    if not os.path.exists(RULES_FILE):
        return {}
    with open(RULES_FILE, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return {}

def save_rules(merchant, category):
    """Saves or updates a merchant-category pair in JSON."""
    rules = load_rules()
    rules[merchant] = category
    with open(RULES_FILE, "w") as file:
        json.dump(rules, file, indent=4)

def cluster_merchants(df, threshold=90):
    """Groups similar merchant names using fuzzy matching."""
    unique_merchants = df["Merchant"].unique()
    clusters = []
    visited = set()

    for merchant in unique_merchants:
        if merchant in visited:
            continue

        cluster = [merchant]
        visited.add(merchant)

        for other in unique_merchants:
            if other in visited:
                continue
            score = fuzz.token_sort_ratio(str(merchant), str(other))
            if score >= threshold:
                cluster.append(other)
                visited.add(other)

        clusters.append(cluster)

    return clusters

def get_category(merchant, rules, threshold=90, model=None, vectorizer=None):
    """
    Determines category using:
    1. Exact match
    2. Fuzzy match
    3. Default fallback
    """
    if merchant in rules:
        return rules[merchant]

    best_match = None
    highest_score = 0

    for known_merchant in rules.keys():
        score = fuzz.token_sort_ratio(str(merchant), str(known_merchant))
        if score > highest_score:
            highest_score = score
            best_match = known_merchant

    if highest_score >= threshold:
        return rules[best_match]
    
    if model is not None and vectorizer is not None:
        predicted_category = predict_category(merchant, model, vectorizer)
        if predicted_category != "UNCATEGORIZED":
            return predicted_category
        
    return "UNCATEGORIZED"

def apply_classification(df):
    """Applies category classification to the dataframe."""
    merchants, categories = build_training_data()
    model, vectorizer = train_model(merchants, categories)
    rules = load_rules()
    rules = load_rules()
    df["Category"] = df["Merchant"].apply(
        lambda x: get_category(x, rules, model=model, vectorizer=vectorizer)
    )
    return df

def build_training_data():
    """Prepares data for ML model training."""
    rules = load_rules()
    merchants = list(rules.keys())
    categories = list(rules.values())
    
    return merchants, categories

def train_model(merchants, categories):
    """Trains a Random Forest classifier on the merchant-category data."""
    
    if len(merchants) < 10:
        return None, None

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(merchants)
    model =  RandomForestClassifier(n_estimators=100, random_state=42)
    
    model.fit(X, categories)
    return model, vectorizer
    
def predict_category(merchant, model, vectorizer):
    """Predicts category for a merchant using the trained model."""
    if model is None or vectorizer is None:
        return "UNCATEGORIZED"
    
    X = vectorizer.transform([merchant])
    predicted_category = model.predict(X)[0]
    return predicted_category
    