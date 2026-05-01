# WealthWise ML

A personal finance tracker for Indian students and retail investors. Upload a bank or UPI transaction CSV and the app automatically cleans the data, categorizes merchants, nets out reimbursements, and shows how your spending lines up against your SIP target.

No data is sent to a server. Everything runs in-memory in your browser session.

Live demo: [wealthwise-ml.streamlit.app](https://wealthwise-ml.streamlit.app)

---

## What it does

**CSV ingestion** — A header sniffer maps bank-specific column names (HDFC, SBI, GPay, Groww) to a standard internal schema. You do not need to reformat your file.

**Merchant extraction** — Strips UPI noise from transaction strings (`UPI/DDSTORE/20260220/1` becomes `DDSTORE`) using regex pattern matching.

**Reimbursement netting** — Detects paired outgoing and incoming amounts within a 7-day window to calculate true spend rather than gross spend.

**Hybrid classification** — Three-stage pipeline: exact match against saved rules, fuzzy match via RapidFuzz, then a Random Forest classifier for unseen merchants. Low-confidence predictions fall back to UNCATEGORIZED rather than guessing.

**Labeling interface** — Groups similar merchants into clusters so you label once and the rule applies to all variants. Labels persist in a local JSON file.

**SIP goal tracking** — Enter your monthly income and SIP target. The dashboard shows how much you have spent, how much is invested, what is left, and whether you are on track.

**AI advisor** — Chat interface powered by Groq (llama-3.3-70b-versatile) that receives your processed transaction data as context and gives advice specific to your numbers.

---

## Tech stack

| Layer | Tool |
|---|---|
| Frontend | Streamlit |
| Data processing | Pandas, NumPy |
| Machine learning | Scikit-learn (Random Forest, TF-IDF) |
| Fuzzy matching | RapidFuzz |
| Visualizations | Plotly |
| AI assistant | Groq API |

---

## Setup

Clone the repo and install dependencies:

```bash
git clone https://github.com/navinvishwa07/WealthWise-ML.git
cd WealthWise-ML
pip install -r requirements.txt
```

Add your Groq API key (the advisor will still work without it, with rule-based tips as fallback):

```bash
cp .env.example .env
# Edit .env and add your key
```

Run:

```bash
streamlit run main.py
```

Get a free Groq API key at [console.groq.com](https://console.groq.com).

---

## Project structure

```
main.py          # Streamlit UI and session state
processor.py     # CSV ingestion, cleaning, reimbursement detection
classifier.py    # Rule loading, fuzzy matching, ML training and inference
ai_advisor.py    # Groq API integration and context builder
logic_engine.py  # Budget math (weekly safe spend, sinking fund)
config.py        # Thresholds, model names, category list
seed_rules.json  # Default merchant-to-category mappings
```

---

## Privacy

Transaction data is processed in-memory and never written to disk, sent to an external server, or logged. The only file written locally is `user_rules.json`, which stores merchant labels you create — no transaction amounts or dates.

---

## License

MIT
