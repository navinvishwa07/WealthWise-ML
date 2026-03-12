import streamlit as st
import pandas as pd
import plotly.express as px
from processor import generate_mock_data, process_data
from classifier import apply_classification, save_rules

# Session state ensures data persists across reruns
# (Streamlit re-executes the script on every interaction)
if "df" not in st.session_state:
    st.session_state.df = None

st.title("WealthWise - Finance Tracking app")

st.sidebar.title("Monthly Income in Rs") 
monthly_income = st.sidebar.number_input("Insert your monthly income")
st.write("The current number is ", monthly_income)

st.sidebar.title("Monthly SIP in Rs")
SIP = st.sidebar.number_input("Insert you SIP amount")
st.write("The current number is ", SIP)

monthly_spending_csv = st.file_uploader(
    "Upload your monthly spending CSV",
    type=["csv", "xlsx"]
)

"""
Use uploaded file if provided
If no upload and no session data → generate mock data
Otherwise reuse session state
"""

if monthly_spending_csv is not None:
    df = pd.read_csv(monthly_spending_csv, on_bad_lines='skip')
    df = process_data(df)
    st.session_state.df = df

elif st.session_state.df is None:
    df = generate_mock_data()
    df = process_data(df)
    st.session_state.df = df

else:
    df = st.session_state.df

# Apply rule-based classification before rendering UI
df = apply_classification(df)

# Tabs help separate logic-heavy sections from display sections
tab1, tab2, tab3 = st.tabs(["Dashboard", "Labeling", "Raw Data"])

with tab1:
    st.subheader("Overview")

    # Exclude transfers and investments from spending calculations
    spending_df = df[~df["is_transfer"] & ~df["is_investment"] & ~df["is_reimbursement"]]
    total_spent = spending_df["Amount"].sum()    
    
    # Food analysis (all categories containing "Food")
    food_df = df[df["Category"].str.contains("Food", na=False)]
    total_food = food_df["Amount"].sum()

    # Category-wise breakdown
    category_summary = (
        spending_df
        .groupby("Category")["Amount"]
        .sum()
        .sort_values(ascending=False)
    )

    # SIP treated as planned investment
    invested = SIP
    remaining_budget = monthly_income - total_spent - invested
    netted_amount = df[df["is_reimbursement"]]["Amount"].abs().sum() / 2

    # ---------------- Core Metrics ----------------
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Spent", f"₹ {total_spent:,.2f}")

    with col2:
        st.metric("SIP (Investment)", f"₹ {invested:,.2f}")

    with col3:
        st.metric("Remaining Budget", f"₹ {remaining_budget:,.2f}")
    with col4:
        st.metric("Reimbursements Netted", f"₹ {netted_amount:,.2f}")

    # SIP progress
    if SIP > 0:
        sip_progress = min(invested / SIP, 1.0)
        st.progress(sip_progress)

    # ---------------- Spending Ratio ----------------
    if monthly_income > 0:
        spending_ratio = (total_spent / monthly_income) * 100
        st.write(f"You have spent {spending_ratio:.1f}% of your monthly income.")

    # ---------------- Top Categories ----------------
    st.subheader("Top Spending Categories")
    st.dataframe(category_summary.head(5))

    # ---------------- Full Category Breakdown ----------------
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

    # ---------------- Food Concentration Insight ----------------
    if total_spent > 0:
        food_ratio = (total_food / total_spent) * 100
        st.write(f"{food_ratio:.1f}% of your total spending is on food.")
    
with tab2:
    st.subheader("Uncategorized Merchants")
    
    # Filter only transactions that still lack a category
    uncategorized_df = df[df["Category"] == "UNCATEGORIZED"]
    unique_merchants = uncategorized_df["Merchant"].unique()
    
    if len(unique_merchants) == 0:
        st.success("All merchants are categorized.")
    else:
        for merchant in unique_merchants:
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.write(merchant)

            with col2:
                category = st.selectbox(
                        "Assign Category",
                        [
                            "Food - College Canteen",
                            "Food - Royal Biryani",
                            "Food - Akka Kadai",
                            "Food - Delivery (Swiggy/Zomato)",
                            "Food - Eating Out (Friends)",
                            "Groceries / Snacks",
                            "Transport - Petrol",
                            "Transport - Rapid / Auto",
                            "Friends Payments",
                            "Sports & Activities",
                            "Personal Care",
                            "Shopping",
                            "Gifts",
                            "Investments (SIP)",
                            "Other"
                        ],
                        key=f"select_{merchant}"
                    )

            with col3:
                if st.button("Save", key=f"save_{merchant}"):
                    save_rules(merchant, category)
                    st.success(f"Saved {merchant} as {category}")
                    st.rerun()

with tab3:
    st.subheader("Raw Transactions")
    st.dataframe(df)
