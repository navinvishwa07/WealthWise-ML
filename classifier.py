import json
import os

import config
from rapidfuzz import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier

RULES_FILE = config.RULES_FILE
DEFAULT_RULES = config.DEFAULT_RULES


def _load_json(path):
    """Load a JSON object from disk and return an empty mapping on bad input."""
    if not os.path.exists(path):
        return {}

    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError):
        return {}

    return data if isinstance(data, dict) else {}


def load_rules():
    """Load seed and user merchant-category mappings.

    User rules override seed rules at runtime, but saving a new label only writes
    to the user rules file so the curated seed rules stay separate.
    """
    seed_rules = _load_json(DEFAULT_RULES)
    user_rules = _load_json(RULES_FILE)
    return {**seed_rules, **user_rules}


def save_rules(merchant, category):
    """Save or update a user merchant-category rule."""
    rules = _load_json(RULES_FILE)
    rules[str(merchant).upper()] = category
    with open(RULES_FILE, "w") as file:
        json.dump(rules, file, indent=4)


def cluster_merchants(df, threshold=config.FUZZY_THRESHOLD):
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


def get_category(merchant, rules, threshold=config.FUZZY_THRESHOLD, model=None, vectorizer=None):
    """
    Determines category using:
    1. Exact match
    2. Fuzzy match
    3. Default fallback
    """
    merchant = str(merchant).upper()

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
        if predicted_category != config.CATEGORY_UNCATEGORIZED:
            return predicted_category
        
    return config.CATEGORY_UNCATEGORIZED


def apply_classification(df):
    """Applies category classification to the dataframe."""
    if "Category" not in df.columns:
        df["Category"] = config.CATEGORY_UNCATEGORIZED

    merchants, categories = build_training_data()
    model, vectorizer = train_model(merchants, categories)
    rules = load_rules()
    mask = df["Category"].isna() | (df["Category"] == config.CATEGORY_UNCATEGORIZED)
    df.loc[mask, "Category"] = df.loc[mask, "Merchant"].apply(
        lambda merchant: get_category(merchant, rules, model=model, vectorizer=vectorizer)
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
    
    if len(merchants) < config.ML_MIN_TRAINING_SAMPLES or len(set(categories)) < 2:
        return None, None

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(merchants)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    
    model.fit(X, categories)
    return model, vectorizer


def predict_category(merchant, model, vectorizer):
    """Predicts category for a merchant using the trained model with confidence filtering."""
    
    if model is None or vectorizer is None:
        return config.CATEGORY_UNCATEGORIZED
    
    X = vectorizer.transform([merchant])
    predicted_category = model.predict(X)[0]
    
    proba = model.predict_proba(X)
    max_confidence = proba.max(axis=1)[0]
    
    if max_confidence < config.ML_CONFIDENCE_THRESHOLD:
        return config.CATEGORY_UNCATEGORIZED
    
    return predicted_category
