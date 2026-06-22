import calendar
import datetime


def weekly_safe_spend(monthly_income, total_spent, sip_target, as_of=None):
    """Calculate weekly discretionary spend left for the current month."""
    as_of = as_of or datetime.date.today()
    remaining_budget = monthly_income - total_spent - sip_target
    _, days_in_month = calendar.monthrange(as_of.year, as_of.month)
    days_remaining = max(days_in_month - as_of.day, 0)
    weeks_remaining = max(days_remaining / 7, 1)
    return remaining_budget / weeks_remaining


def sinking_fund_calc(goal_amount, months):
    """Calculate the monthly saving required to hit a goal."""
    if months <= 0:
        raise ValueError("months must be greater than zero")

    return goal_amount / months
