markdown
# Hybrid Transaction Classification & RAG Finance Assistant

A personal finance tracker for Indian students and retail investors. Ingests bank and UPI transaction exports, classifies merchants using a hybrid rule-based and ML pipeline, nets out reimbursements, tracks SIP progress, and answers finance questions through a RAG pipeline grounded in the user's actual transaction history.

Live demo: [wealthwise-ml.streamlit.app](https://wealthwise-ml.streamlit.app)

---

## What it does

**Agnostic CSV/XLSX ingestion** — A header sniffer maps varied bank export formats (HDFC, SBI, GPay, Groww) to a standard internal schema using exact match first, fuzzy match as fallback.

**Merchant extraction** — Strips UPI noise from transaction strings (`UPI/DDSTORE/20260220/1` becomes `DDSTORE`) using regex pattern matching.

**Reimbursement netting** — Detects paired outgoing/incoming amounts within a 7-day window, so money paid back by a friend doesn't inflate spending totals.

**Hybrid classification** — Three-stage pipeline: exact match against saved rules, fuzzy match via RapidFuzz, then a confidence-gated Random Forest classifier (TF-IDF features) for unseen merchants. Low-confidence predictions fall back to `UNCATEGORIZED` rather than guessing wrong.

**Labeling interface** — Groups similar uncategorized merchants into fuzzy clusters so a label applies once to every variant. Labels persist locally in `user_rules.json`.

**SIP goal tracking** — Enter monthly income and SIP target. The dashboard shows spend, investment progress, remaining budget, and weekly safe-spend pacing.

**Model evaluation** — Tests the classifier against saved rules and reports accuracy, per-category precision/recall/F1, and a confusion matrix, so classifier quality is measured rather than assumed.

**Semantic transaction search** — A standalone search tab that finds transactions by meaning rather than exact keywords, using vector similarity over transaction embeddings.

**RAG-powered AI advisor** — A chat interface backed by Groq (`llama-3.3-70b-versatile`). Transactions are embedded with sentence-transformers and stored in ChromaDB; at query time, the most relevant transactions — and any finance PDFs the user has uploaded — are retrieved and passed to the LLM as context via LangChain. Answers reference actual transaction data instead of generic advice.

---

## Tech stack

| Layer | Tool |
|---|---|
| Frontend | Streamlit |
| Data processing | Pandas, NumPy, Regex |
| Machine learning | Scikit-learn (Random Forest, TF-IDF), evaluated via precision/recall/F1/confusion matrix |
| Fuzzy matching | RapidFuzz |
| Visualizations | Plotly |
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`) |
| Vector store | ChromaDB |
| RAG orchestration | LangChain |
| LLM | Groq (`llama-3.3-70b-versatile`) |
| PDF parsing | pypdf |

---

## Setup

bash
git clone https://github.com/navinvishwa07/Hybrid-Transaction-Classification-RAG-Finance-Assistant.git
cd Hybrid-Transaction-Classification-RAG-Finance-Assistant
pip install -r requirements.txt


Add your Groq API key:

bash
cp .env.example .env
# Edit .env and add your key


Run:

bash
streamlit run main.py


Get a free Groq API key at [console.groq.com](https://console.groq.com).

---

## Usage

1. Enter monthly income and SIP target in the sidebar.
2. Upload a `.csv` or `.xlsx` transaction export, or use the bundled mock data.
3. Review **Dashboard** for spend, SIP progress, reimbursements, and category breakdown.
4. Use **Labeling** to categorize uncategorized merchant clusters — the classifier improves as more merchants are labeled.
5. Check **Evaluation** to see classifier accuracy, precision/recall/F1, and the confusion matrix.
6. Use **Semantic Search** to find transactions by meaning.
7. Ask the **AI Advisor** finance questions, optionally after uploading a finance PDF for extra context.

---

## Project structure

main.py               Streamlit UI: session state, dashboard, labeling, search, advisor, eval
processor.py           CSV/XLSX ingestion, cleaning, merchant extraction, reimbursement detection
classifier.py          Rule loading/saving, fuzzy matching, Random Forest training and inference
embedding.py            Transaction-to-sentence templating and vector embedding (lazy-loaded model)
vector_store.py           ChromaDB transaction collection: store and similarity search
knowledge_base.py          PDF ingestion, chunking, embedding, and retrieval
semantic_search.py          Standalone semantic search over transaction embeddings
rag_advisor.py                LangChain chain wiring ChromaDB retrieval to Groq
evaluator.py                   Classifier evaluation: precision, recall, F1, confusion matrix
logic_engine.py                 Budget math: weekly safe spend, sinking fund calculation
config.py                        Thresholds, categories, model names, collection names
seeds_rules.json                  Built-in merchant-to-category defaults
user_rules.json                    User-saved merchant labels (gitignored)


---

## Privacy

Transaction data is processed in-memory within the Streamlit session and never sent to an external server except as retrieved context in an explicit AI Advisor query. Locally persisted files:

- `user_rules.json` — merchant labels created by the user (no amounts or dates)
- `./chroma_db` — transaction and document embeddings used for semantic retrieval

If the AI Advisor tab is never used, no LLM request is made.

---

## License

MIT