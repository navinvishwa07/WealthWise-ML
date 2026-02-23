import json
import os

RULES_FILE = "user_rules.json"

def load_rules():
    if os.path.exists(RULES_FILE):
        return {}
    
    with open(RULES_FILE, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return {}
        
def save_rules(merchant,category):
    rules = load_rules()
    rules[merchant] = category

    with open(RULES_FILE, "w") as file:
        json.dump(rules, file, indent=4)