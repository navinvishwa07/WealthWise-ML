import pandas as pd
import plotly.express as px
import streamlit as st

from classifier import apply_classification, cluster_merchants, save_rules
from config import CATEGORIES, CATEGORY_UNCATEGORIZED
from embedding import embed_transactions
from logic_engine import weekly_safe_spend
from processor import generate_mock_data, process_data
from vector_store import store_embeddings
from evaluator import evaluate_classifier


APP_TITLE = "WealthWise"
SUPPORTED_UPLOAD_TYPES = ["csv", "xlsx"]


def initialize_session_state():
    """Initialize Streamlit session state used across tabs."""
    defaults = {
        "df": None,
        "clusters": None,
        "embedded_df": None,
        "embedded_fingerprint": None,
        "uploaded_file_signature": None,
    }

    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def load_uploaded_transactions(uploaded_file):
    """Read a CSV/XLSX upload and normalize it into WealthWise's schema."""
    filename = uploaded_file.name.lower()

    if filename.endswith(".xlsx"):
        raw_df = pd.read_excel(uploaded_file)
    else:
        raw_df = pd.read_csv(uploaded_file, on_bad_lines="skip")

    return process_data(raw_df)


def dataframe_fingerprint(df):
    """Create a stable fingerprint for transaction data in the current session."""
    hashable_df = df.drop(columns=["embedding"], errors="ignore").astype(str)
    return str(pd.util.hash_pandas_object(hashable_df, index=True).sum())


def get_prepared_transactions(df):
    """Classify, embed, and store transactions only when the data changes."""
    classified_df = apply_classification(df.copy())
    fingerprint = dataframe_fingerprint(classified_df)

    if st.session_state.embedded_fingerprint == fingerprint:
        return st.session_state.embedded_df.copy()

    embedded_df = embed_transactions(classified_df)
    store_embeddings(embedded_df)
    st.session_state.embedded_df = embedded_df
    st.session_state.embedded_fingerprint = fingerprint
    return embedded_df.copy()


def invalidate_prepared_transactions():
    """Clear cached derived data after labels or source transactions change."""
    st.session_state.clusters = None
    st.session_state.embedded_df = None
    st.session_state.embedded_fingerprint = None


def render_sidebar():
    st.sidebar.title("Monthly Plan")
    monthly_income = st.sidebar.number_input(
        "Monthly income",
        min_value=0.0,
        step=500.0,
        format="%.0f",
    )
    monthly_sip = st.sidebar.number_input(
        "Monthly SIP target",
        min_value=0.0,
        step=500.0,
        format="%.0f",
    )
    return monthly_income, monthly_sip


def render_upload_section():
    uploaded_file = st.file_uploader(
        "Upload your monthly spending file",
        type=SUPPORTED_UPLOAD_TYPES,
    )

    if uploaded_file is None:
        return

    file_signature = (uploaded_file.name, uploaded_file.size)
    if st.session_state.uploaded_file_signature == file_signature:
        return

    try:
        st.session_state.df = load_uploaded_transactions(uploaded_file)
        st.session_state.uploaded_file_signature = file_signature
        invalidate_prepared_transactions()
        st.success("Transactions loaded successfully.")
    except Exception as exc:
        st.error(f"Could not process this file: {exc}")


def render_dashboard(df, monthly_income, monthly_sip):
    st.subheader("Overview")

    spending_df = df[
        ~df["is_transfer"]
        & ~df["is_investment"]
        & ~df["is_reimbursement"]
    ]
    total_spent = spending_df["Amount"].sum()
    invested = df[df["is_investment"]]["Amount"].sum()
    remaining_budget = monthly_income - total_spent - invested
    netted_amount = df[df["is_reimbursement"]]["Amount"].abs().sum() / 2
    weekly_spend = weekly_safe_spend(monthly_income, total_spent, monthly_sip)

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Spent", f"₹{total_spent:,.0f}")
    col2.metric("Invested", f"₹{invested:,.0f}")
    col3.metric("Remaining Budget", f"₹{remaining_budget:,.0f}")
    col4.metric("Reimbursements Netted", f"₹{netted_amount:,.0f}")
    col5.metric("Weekly Safe Spend", f"₹{weekly_spend:,.0f}")

    if monthly_sip > 0:
        st.progress(min(max(invested / monthly_sip, 0.0), 1.0))

    if monthly_income > 0:
        spending_ratio = (total_spent / monthly_income) * 100
        st.write(f"You have spent {spending_ratio:.1f}% of your monthly income.")

    category_summary = (
        spending_df
        .groupby("Category")["Amount"]
        .sum()
        .sort_values(ascending=False)
    )

    if category_summary.empty:
        st.info("No spend transactions to chart yet.")
    else:
        pie_graph = px.pie(
            values=category_summary.values,
            names=category_summary.index,
            hole=0.4,
            title="Spending by Category",
        )
        st.plotly_chart(pie_graph, use_container_width=True)

    if not spending_df.empty:
        daily_spend = (
            spending_df
            .groupby("Date")["Amount"]
            .sum()
            .cumsum()
            .reset_index()
        )
        daily_spend["Projected"] = pd.Series(
            data=[
                index * ((monthly_income - monthly_sip) / max(len(daily_spend) - 1, 1))
                for index in range(len(daily_spend))
            ],
            index=daily_spend.index,
        )
        daily_spend.columns = ["Date", "Cumulative Spend", "Projected"]
        line_graph = px.line(
            daily_spend,
            x="Date",
            y=["Cumulative Spend", "Projected"],
            title="Cumulative Spending This Month",
        )
        st.plotly_chart(line_graph, use_container_width=True)

    st.subheader("Category Spending Breakdown")

    if total_spent > 0:
        for category, amount in category_summary.items():
            percent = (amount / total_spent) * 100
            col_left, col_right = st.columns([3, 1])
            col_left.write(category)
            col_left.progress(max(0.0, min(percent / 100, 1.0)))
            col_right.write(f"{percent:.1f}%")

        food_total = df[
            df["Category"].str.contains("FOOD", case=False, na=False)
        ]["Amount"].sum()
        food_ratio = (food_total / total_spent) * 100
        st.write(f"{food_ratio:.1f}% of your total spending is on food.")

    canteen_count = df[df["Merchant"].isin(["DD", "DDSTORE"])].shape[0]
    if canteen_count > 5:
        st.warning(f"⚠️ High canteen frequency — {canteen_count} visits this month.")


def render_labeling_tab(df):
    st.subheader("Uncategorized Merchants")

    uncategorized_df = df[df["Category"] == CATEGORY_UNCATEGORIZED]
    unique_merchants = set(uncategorized_df["Merchant"].unique())

    if not unique_merchants:
        st.success("All merchants are categorized.")
        return

    if st.button("Refresh clusters"):
        st.session_state.clusters = None
        st.rerun()

    if st.session_state.clusters is None:
        with st.spinner("Clustering merchants..."):
            st.session_state.clusters = cluster_merchants(df)

    for cluster in st.session_state.clusters:
        cluster_uncategorized = [merchant for merchant in cluster if merchant in unique_merchants]

        if not cluster_uncategorized:
            continue

        cluster_key = "_".join(cluster_uncategorized)
        col1, col2, col3 = st.columns([3, 2, 1])
        col1.write(", ".join(cluster))

        category = col2.selectbox(
            "Assign category",
            CATEGORIES,
            key=f"select_{cluster_key}",
        )

        if col3.button("Save", key=f"save_{cluster_key}"):
            for merchant in cluster:
                save_rules(merchant, category)
                df.loc[df["Merchant"] == merchant, "Category"] = category

            st.session_state.df = df.drop(columns=["sentence", "embedding"], errors="ignore")
            invalidate_prepared_transactions()
            st.success(f"Saved {len(cluster)} merchant variants as {category}.")
            st.rerun()


def render_raw_data_tab(df):
    st.subheader("Raw Transactions")
    display_df = df.drop(columns=["embedding"], errors="ignore")
    st.dataframe(display_df, use_container_width=True)


def render_ai_advisor_tab():
    st.subheader("AI Financial Advisor")
    st.caption(
        "Uses your stored transaction embeddings and optional PDF knowledge base "
        "to answer finance questions through Groq."
    )

    uploaded_doc = st.file_uploader(
        "Upload a finance document (PDF)",
        type=["pdf"],
        key="kb_upload",
    )

    if uploaded_doc is not None:
        from knowledge_base import load_document

        chunks_stored = load_document(uploaded_doc, uploaded_doc.name)
        st.success(f"Loaded {chunks_stored} chunks from {uploaded_doc.name}.")

    user_question = st.text_input("Ask me anything about your finances...")

    if not st.button("Ask"):
        return

    if not user_question:
        st.warning("Please enter a question.")
        return

    with st.spinner("Thinking..."):
        try:
            from rag_advisor import ask_rag

            response = ask_rag(user_question)
            st.write(response)
        except RuntimeError as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(f"AI advisor failed: {exc}")

def render_evaluation_tab():
    st.subheader("Classifier Evaluation")

    report, matrix, labels, y_pred = evaluate_classifier()

    if report is None:
        st.warning("Not enough labeled merchants to evaluate the classifier.")
        return

    # Overall accuracy
    st.metric("Accuracy", f"{report['accuracy'] * 100:.2f}%")

    st.subheader("Classification Report")

    report_df = (
        pd.DataFrame(report)
        .transpose()
        .round(3)
    )

    st.dataframe(report_df, use_container_width=True)

    st.subheader("Confusion Matrix")

    matrix_df = pd.DataFrame(
        matrix,
        index=labels,
        columns=labels,
    )

    st.dataframe(matrix_df, use_container_width=True)

def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="💸", layout="wide")
    initialize_session_state()

    st.title("WealthWise - Finance Tracker")
    monthly_income, monthly_sip = render_sidebar()
    render_upload_section()

    if st.session_state.df is None:
        st.info("Using mock transactions. Upload a CSV or XLSX file to analyze your own data.")
        st.session_state.df = process_data(generate_mock_data())

    df = get_prepared_transactions(st.session_state.df)
    tab_dashboard, tab_labeling, tab_raw, tab_ai, tab_evaluation = st.tabs(
    [
        "Dashboard",
        "Labeling",
        "Raw Data",
        "AI Advisor",
        "Evaluation",
    ]
)

    with tab_dashboard:
        render_dashboard(df, monthly_income, monthly_sip)

    with tab_labeling:
        render_labeling_tab(df)

    with tab_raw:
        render_raw_data_tab(df)

    with tab_ai:
        render_ai_advisor_tab()
        
    with tab_evaluation:
        render_evaluation_tab()


if __name__ == "__main__":
    main()
