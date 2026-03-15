# 💰 WealthWise ML

WealthWise ML is a privacy-first personal finance platform built for Indian retail investors and students. It automatically classifies UPI and bank transactions using Machine Learning and Fuzzy Logic, then surfaces actionable savings insights — all without a single rupee of your data leaving your device.

---

## ✨ Features

- **Agnostic CSV Ingestion** — A header sniffer that maps bank-specific column names (HDFC, SBI, GPay, Groww) to a unified internal schema automatically
- **Reimbursement Netting Engine** — Detects paired outgoing/incoming amounts (e.g. -₹514 / +₹514) to calculate your *true* spend, not inflated totals
- **Fuzzy Merchant Clustering** — Groups similar-but-messy UPI strings (`DDSTORE-01`, `DD-STORE-99`) into single clusters for one-shot labeling
- **"Remember Me" JSON Rules Engine** — Saves your merchant → category mappings locally so you never re-label the same merchant twice
- **Random Forest Classifier** — Learns from your saved rules to predict categories for new, unseen merchants
- **SIP Goal Tracker** — Monitors your actual spending against a custom income and monthly SIP target (e.g. ₹2,000 SIP on ₹5,000 budget)
- **Budget Gap Analysis** — Visualizes the variance between actual monthly spend and projected future spend
- **Contextual AI Assistant** — A chat interface powered by Groq that receives your processed transaction data as context for personalized savings advice

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Data Processing | Pandas, NumPy, Regex |
| Machine Learning | Scikit-learn (Random Forest, TF-IDF) |
| Fuzzy Matching | RapidFuzz |
| Visualizations | Plotly |
| AI Assistant | Groq API |
| Performance | Python `threading` |

---

## ⚙️ Setup

1. **Clone the repo**
   ```bash
   git clone git clone https://github.com/navinvishwa07/WealthWise-ML.git
   cd wealthwise-ml
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Add your Groq API key**

   Create a `.env` file in the project root:
   ```
   GROQ_API_KEY=your_key_here
   ```

4. **Run the app**
   ```bash
   streamlit run main.py
   ```

---

## 🔒 Privacy

All transaction data is processed entirely in-memory within your browser session — nothing is sent to a server, stored in a database, or shared externally.

---

## 🔑 Get a Groq API Key

Sign up and generate a free API key at [console.groq.com](https://console.groq.com).