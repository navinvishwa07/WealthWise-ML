import streamlit as st
import pandas as pd
from processor import generate_mock_data, process_data
from classifier import apply_classification


# Session state ensures data persists across reruns
# (Streamlit re-executes the script on every interaction)
if "df" not in st.session_state:
    st.session_state.df = None

st.title("WealthWise - Finance Tracking app using ML")

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
    df = pd.read_csv(monthly_spending_csv)
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
    st.write("Summary insights will go here.")

with tab2:
    st.subheader("Uncategorized Merchants")

    # Filter only transactions that still lack a category
    uncategorized_df = df[df["Category"] == "UNCATEGORIZED"]
    unique_merchants = uncategorized_df["Merchant"].unique()

    for merchant in unique_merchants:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(merchant)
        with col2:
            category = st.selectbox(
                "Assign Category",
                ["Food", "Transport", "Bills", "Shopping", "Other"],
                key=merchant
            )

with tab3:
    st.subheader("Raw Transactions")
    st.dataframe(df)
