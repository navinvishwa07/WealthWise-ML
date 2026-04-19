# --- Classification thresholds ---
FUZZY_THRESHOLD = 80
ML_CONFIDENCE_THRESHOLD = 0.75
ML_MIN_TRAINING_SAMPLES = 50

# --- Categories ---
CATEGORIES = [
    "food",
    "transport",
    "shopping",
    "entertainment",
    "utilities",
    "health",
    "education",
    "travel",
    "other"
]

# --- Rules configuration ---
RULES_FILE = "user_rules.json"
DEFAULT_RULES = "seed_rules.json"

# --- Reimbursement logic ---
REIMBURSEMENT_WINDOW_DAYS = 7
REIMBURSEMENT_AMOUNT_TOLERANCE = 1

# --- AI model configuration ---
GROQ_MODEL = "llama-3.3-70b-versatile"