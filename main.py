import streamlit as st
import pandas as pd
from processor import generate_mock_data, process_data

# Initialize session state for data persistence
if "df" not in st.session_state:
    st.session_state.df = None

st.title("WealthWise - Finance Tracking app using ML")

st.sidebar.title("Monthly Income in Rs")
monthly_income = st.sidebar.number_input("Insert your monthly income")
st.write("The current number is ", monthly_income)

st.sidebar.title("Monthly SIP in Rs")
SIP = st.sidebar.number_input("Insert you SIP amount")
st.write("The current number is ", SIP)

monthly_spending_csv = st.file_uploader("Upload your monthly spending CSV", type=["csv", "xlsx"])

if monthly_spending_csv is not None:
    df = pd.read_csv(monthly_spending_csv)
    df = process_data(df)
    st.session_state.df = df  # Store in session state for later use
elif st.session_state.df is None:
    df = generate_mock_data()
    df = process_data(df)
    st.session_state.df = df
else:
    df = st.session_state.df
    
st.write("Transactions: ", df)

