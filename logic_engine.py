import datetime

def weekly_safe_spend(monthly_income, total_spent, SIP):
    remaining_budget = monthly_income - total_spent - SIP
    days_remaining = 30 - datetime.datetime.now().day
    weeks_remaining = max(days_remaining / 7, 1)
    return remaining_budget / weeks_remaining

def sinking_fund_calc(goal_amount, months):
    monthly_saving = goal_amount / months
    return monthly_saving
