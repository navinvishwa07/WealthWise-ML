import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix
from classifier import load_rules, train_model, build_training_data, get_category


def evaluate_classifier():

    rules = load_rules()

    if len(rules) < 10:
        return None, None, None, None

    merchants = list(rules.keys())
    y_true = list(rules.values())

    trained_merchants, trained_categories = build_training_data()
    model, vectorizer = train_model(trained_merchants, trained_categories)

    y_pred = [
        get_category(merchant, rules, model=model, vectorizer=vectorizer)
        for merchant in merchants
    ]

    labels = sorted(set(y_true))
    report = classification_report(y_true, y_pred, labels=labels, output_dict=True, zero_division=0)
    matrix = confusion_matrix(y_true, y_pred, labels=labels)

    return report, matrix, labels, y_pred