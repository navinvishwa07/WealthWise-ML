# WealthWise ML

WealthWise ML is a Streamlit-based personal finance tracker for Indian students and retail investors. It ingests bank, UPI, CSV, or Excel transaction exports, cleans messy descriptions, categorizes merchants, nets reimbursements, tracks SIP progress, and offers a RAG-powered AI advisor over your transaction context.

Live demo: [wealthwise-ml.streamlit.app](https://wealthwise-ml.streamlit.app)

## Features

- **Flexible ingestion**: Detects common bank/export headers such as `Date`, `Txn Date`, `Narration`, `Description`, `Amount`, `Debit`, and `Withdrawal Amt`.
- **Merchant cleanup**: Normalizes noisy UPI descriptions like `UPI/DDSTORE/20260220/1` into clean merchant names such as `DDSTORE`.
- **Hybrid classification**: Applies seed rules, user-saved rules, fuzzy matching, and a confidence-gated Random Forest model for unknown merchants.
- **Labeling workflow**: Clusters similar uncategorized merchants so one label can apply to multiple variants.
- **Reimbursement detection**: Finds opposite-signed personal payment pairs within a configurable date and amount window.
- **Dashboard metrics**: Shows spending, investments, remaining budget, reimbursements netted, weekly safe spend, category splits, and cumulative spend.
- **RAG advisor**: Embeds transactions with Sentence Transformers, stores them in ChromaDB, retrieves relevant context, and uses Groq through LangChain for grounded answers.
- **PDF knowledge base**: Lets you upload finance PDFs that are chunked, embedded, and retrieved alongside transactions.

## Tech Stack

| Layer | Tool |
|---|---|
| App UI | Streamlit |
| Data processing | Pandas |
| Charts | Plotly |
| Classification | Scikit-learn, RapidFuzz |
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`) |
| Vector store | ChromaDB |
| RAG orchestration | LangChain |
| LLM provider | Groq (`llama-3.3-70b-versatile`) |
| PDF parsing | pypdf |

## Setup

```bash
git clone https://github.com/navinvishwa07/WealthWise-ML.git
cd WealthWise-ML
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add your Groq API key to `.env`:

```bash
GROQ_API_KEY=your_groq_api_key
```

Run the app:

```bash
streamlit run main.py
```

You can get a Groq API key from [console.groq.com](https://console.groq.com).

## Usage

1. Open the Streamlit app.
2. Enter your monthly income and SIP target in the sidebar.
3. Upload a `.csv` or `.xlsx` transaction export, or use the bundled mock data.
4. Review the dashboard for spend, SIP progress, reimbursements, and category breakdowns.
5. Use the **Labeling** tab to categorize uncategorized merchant clusters.
6. Use the **AI Advisor** tab to ask finance questions, optionally after uploading a PDF knowledge source.

## Expected Data

WealthWise expects transaction data with recognizable date, description, and amount columns. The header sniffer maps common variants into this internal schema:

| Internal Field | Examples |
|---|---|
| `Date` | `Date`, `Txn Date`, `Transaction Date`, `Value Date`, `Posting Date` |
| `Description` | `Description`, `Narration`, `Transaction Remarks`, `Remarks`, `Details`, `Particulars` |
| `Amount` | `Amount`, `Withdrawal Amt`, `Debit`, `Dr Amount`, `Transaction Amount`, `Withdrawal Amt (INR)` |

Amounts are cleaned into numeric values. Opposite signs are used to identify reimbursement pairs, so exports that split debit and credit columns may need preprocessing before upload.

## Project Structure

```text
main.py              Streamlit UI, session state, dashboard, labeling, AI advisor
processor.py         Header sniffing, cleaning, merchant extraction, reimbursement flags
classifier.py        Rule loading, fuzzy matching, ML training, merchant classification
embedding.py         Lazy SentenceTransformer loading and transaction embeddings
vector_store.py      ChromaDB transaction collection and similarity search
knowledge_base.py    PDF extraction, chunking, embedding, and retrieval
rag_advisor.py       Lazy Groq/LangChain RAG chain
logic_engine.py      Budget and saving calculations
config.py            Thresholds, categories, model names, collection names
seeds_rules.json     Built-in merchant/category rules
user_rules.json      Locally saved merchant labels
test_rag_advisor.py  Local RAG dependency smoke check
```

## Validation

Run a syntax check:

```bash
python -m py_compile main.py processor.py classifier.py embedding.py vector_store.py knowledge_base.py rag_advisor.py logic_engine.py config.py test_rag_advisor.py
```

Run the RAG smoke check:

```bash
python test_rag_advisor.py
```

## Privacy Notes

- Uploaded transaction files are processed in the Streamlit session.
- Merchant labeling rules are saved locally in `user_rules.json`.
- Transaction sentences and embeddings are persisted locally in `./chroma_db` for semantic retrieval.
- The AI Advisor sends your question plus retrieved transaction/PDF context to Groq when you click **Ask**.
- If you do not use the AI Advisor, no LLM request is made.

## License

MIT
