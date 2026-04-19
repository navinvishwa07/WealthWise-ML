import streamlit as st
import pandas as pd
import numpy as np
import threading
import plotly.express as px

from processor import generate_mock_data, process_data
from classifier import apply_classification, save_rules, cluster_merchants
from ai_advisor import get_context, ask_groq
from logic_engine import weekly_safe_spend, sinking_fund_calc

if "df" not in st.session_state:
    st.session_state.df = None

st.title("WealthWise - Finance Tracking app")

st.sidebar.title("Monthly Income in Rs")
monthly_income = st.sidebar.number_input("Insert your monthly income")
st.write("The current number is ", monthly_income)

st.sidebar.title("Monthly SIP in Rs")
SIP = st.sidebar.number_input("Insert your SIP amount")
st.write("The current number is ", SIP)

monthly_spending_csv = st.file_uploader(
    "Upload your monthly spending CSV",
    type=["csv", "xlsx"]
)

if monthly_spending_csv is not None:
    try:
        df = pd.read_csv(monthly_spending_csv, on_bad_lines='skip')
        df = process_data(df)
        st.session_state.df = df
    except Exception as e:
        st.error(f"Error processing file: {e}")

if st.session_state.df is None:
    df = generate_mock_data()
    df = process_data(df)
    st.session_state.df = df

df = st.session_state.df
df = apply_classification(df)

if "clusters" not in st.session_state:
    result = {}
    
    def run_clustering():
        """Runs cluster_merchants in a background thread and stores result."""
        result["clusters"] = cluster_merchants(df)
    
    with st.spinner("Clustering merchants..."):
        """Start thread and wait for it to finish before proceeding."""
        thread = threading.Thread(target=run_clustering)
        thread.start()
        thread.join()
    
    st.session_state.clusters = result["clusters"]
    
    
tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Labeling", "Raw Data", "AI Advisor"])

with tab1:
    st.subheader("Overview")

    spending_df = df[~df["is_transfer"] & ~df["is_investment"] & ~df["is_reimbursement"]]
    total_spent = spending_df["Amount"].sum()
    daily_spend = spending_df.groupby("Date")["Amount"].sum().cumsum().reset_index()
    daily_spend["Projected"] = np.linspace(0, monthly_income - SIP, len(daily_spend))
    daily_spend.columns = ["Date", "Cumulative Spend", "Projected"]
    
    food_df = df[df["Category"].str.contains("Food", na=False)]
    total_food = food_df["Amount"].sum()

    category_summary = (
        spending_df
        .groupby("Category")["Amount"]
        .sum()
        .sort_values(ascending=False)
    )
    
    invested = df[df["is_investment"]]["Amount"].sum()
    remaining_budget = monthly_income - total_spent - invested
    netted_amount = df[df["is_reimbursement"]]["Amount"].abs().sum() / 2

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Total Spent", f"₹ {total_spent:,.2f}")
    with col2:
        st.metric("SIP (Investment)", f"₹ {invested:,.2f}")
    with col3:
        st.metric("Remaining Budget", f"₹ {remaining_budget:,.2f}")
    with col4:
        st.metric("Reimbursements Netted", f"₹ {netted_amount:,.2f}")
    with col5:
        weekly_spend = weekly_safe_spend(monthly_income, total_spent, SIP)
        st.metric("Weekly Safe Spend", f"₹ {weekly_spend:,.2f}")

    if SIP > 0:
        sip_progress = min(invested / SIP, 1.0)
        st.progress(sip_progress)

    if monthly_income > 0:
        spending_ratio = (total_spent / monthly_income) * 100
        st.write(f"You have spent {spending_ratio:.1f}% of your monthly income.")

    pie_graph = px.pie(
    values=category_summary.values,
    names=category_summary.index,
    hole=0.4,
    title="Spending by Category"
    )
    st.plotly_chart(pie_graph)
    
    line_graph = px.line(daily_spend, x = "Date", y = ["Cumulative Spend","Projected"], title="Cumulative Spending This month")
    st.plotly_chart(line_graph)

    st.subheader("Category Spending Breakdown")

    if total_spent > 0:
        for category, amount in category_summary.items():
            percent = (amount / total_spent) * 100
            colA, colB = st.columns([3, 1])
            with colA:
                st.write(category)
                st.progress(percent / 100)
            with colB:
                st.write(f"{percent:.1f}%")

    if total_spent > 0:
        food_ratio = (total_food / total_spent) * 100
        st.write(f"{food_ratio:.1f}% of your total spending is on food.")
        
    canteen_count = df[df["Merchant"].isin(["DD", "DDSTORE"])].shape[0]
    if canteen_count > 5:
        st.warning(f"⚠️ High canteen frequency — {canteen_count} visits this month!")

with tab2:
    st.subheader("Uncategorized Merchants")

    uncategorized_df = df[df["Category"] == "UNCATEGORIZED"]
    unique_merchants = set(uncategorized_df["Merchant"].unique())
    clusters = st.session_state.clusters

    if len(unique_merchants) == 0:
        st.success("All merchants are categorized.")
    else:
        for cluster in clusters:
            # Only show clusters that have at least one uncategorized merchant
            cluster_uncategorized = [m for m in cluster if m in unique_merchants]
            if not cluster_uncategorized:
                continue

            col1, col2, col3 = st.columns([3, 2, 1])

            with col1:
                # Show all merchants in the cluster
                st.write(", ".join(cluster))

            with col2:
                category = st.selectbox(
                    "Assign Category",
                    [
                        "CANTEEN FOOD",
                        "FOOD",
                        "FOOD DELIVERY",
                        "GROCERIES DELIVERY",
                        "TRANSPORT",
                        "CAB BOOKING",
                        "FRIENDS PAYMENTS",
                        "SPORTS & ACTIVITIES",
                        "PERSONAL CARE",
                        "ONLINE SHOPPING",
                        "GIFTS",
                        "INVESTMENTS",
                        "ENTERTAINMENT",
                        "EDUCATION",
                        "RAILWAY BOOKING",
                        "BUS BOOKING",
                        "TRAVEL BOOKING",
                        "FITNESS",
                        "BEAUTY",
                        "OTHER"
                    ],
                    key=f"select_{cluster[0]}"
                )
             

            with col3:
                if st.button("Save", key=f"save_{cluster[0]}"):
                    # Save all merchants in the cluster with the same category
                    for m in cluster:
                        save_rules(m, category)
                    st.success(f"Saved {len(cluster)} merchants as {category}")
                    st.session_state.clusters = None
                    st.rerun()
                    
with tab3:
    st.subheader("Raw Transactions")
    st.dataframe(df)
    
with tab4:
    st.subheader("AI Financial Advisor")
    
    user_question = st.text_input("Ask me anything about your finances...")
    
    if st.button("Ask"):
        if user_question:
            with st.spinner("Thinking..."):
                context = get_context(df, monthly_income, SIP)
                response = ask_groq(user_question, context)
            st.write(response)
        else:
            st.warning("Please enter a question.")