import os
from groq import Groq
from dotenv import load_dotenv

def ask_groq(prompt, context):
    """Sends a prompt to Groq API with financial context as system prompt."""
    load_dotenv()
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": context},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def get_context(df, monthly_income, SIP):
    spending_df = df[~df["is_transfer"] & ~df["is_investment"] & ~df["is_reimbursement"]]
    total_spent = spending_df["Amount"].sum()
    remaining_budget = monthly_income - total_spent - SIP
    spending_ratio = (total_spent / monthly_income * 100) if monthly_income > 0 else 0
    netted = df[df["is_reimbursement"]]["Amount"].abs().sum() / 2
    uncategorized = df[df["Category"] == "UNCATEGORIZED"]["Merchant"].unique().tolist()
    top_categories = spending_df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
    food_df = spending_df[spending_df["Category"].str.contains("Food", na=False)]
    total_food = food_df["Amount"].sum()
    food_ratio = (total_food / total_spent * 100) if total_spent > 0 else 0
    investment_df = df[df["is_investment"]]
    total_invested = investment_df["Amount"].sum()
    sip_gap = SIP - total_invested
    transaction_count = len(spending_df)
    avg_transaction = total_spent / transaction_count if transaction_count > 0 else 0
    largest_transaction = spending_df.nlargest(1, "Amount")[["Merchant", "Amount"]].to_string(index=False) if len(spending_df) > 0 else "None"
    most_frequent_merchant = spending_df["Merchant"].value_counts().head(3).to_string() if len(spending_df) > 0 else "None"

    context = f"""
You are WealthWise, a personal finance advisor specializing in helping Indian students 
manage their finances on a tight budget. You have access to the user's full transaction 
data for this month. Be specific, actionable, and reference exact numbers from their data.

=== FINANCIAL SNAPSHOT ===
Monthly Income:        ₹{monthly_income:,.2f}
SIP Target:            ₹{SIP:,.2f}
Total Spent:           ₹{total_spent:,.2f}
Remaining Budget:      ₹{remaining_budget:,.2f}
Spending Ratio:        {spending_ratio:.1f}% of monthly income

=== INVESTMENT STATUS ===
Amount Invested:       ₹{total_invested:,.2f}
SIP Gap:               ₹{sip_gap:,.2f} {'(ON TRACK)' if sip_gap <= 0 else '(BEHIND TARGET)'}
Reimbursements Netted: ₹{netted:,.2f}

=== SPENDING BREAKDOWN ===
Total Transactions:    {transaction_count}
Average Transaction:   ₹{avg_transaction:,.2f}
Food Spending:         ₹{total_food:,.2f} ({food_ratio:.1f}% of total spend)

Category Breakdown:
{top_categories.to_string()}

=== MERCHANT INSIGHTS ===
Largest Transaction:
{largest_transaction}

Most Frequent Merchants:
{most_frequent_merchant}

=== UNCATEGORIZED MERCHANTS ===
{', '.join(uncategorized) if uncategorized else 'All merchants categorized'}

=== CONTEXT ===
- Target user is a 2nd year Data Science student in Chennai, India
- Monthly allowance is ₹5,000 with a ₹2,000 SIP target
- High frequency merchants include DD Store (college canteen), Swiggy, Zomato
- Any advice should be practical, specific to Indian student life, and reference actual numbers
- If spending ratio exceeds 80%, flag it as a warning
- Always end with 2-3 specific, actionable tips based on the data
"""
    return context