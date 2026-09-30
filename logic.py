"""Credit-health calculations (Indian 300-900 score scale)."""
from models import FinancialRecord


def dti(income: float, debt_payments: float) -> float:
    return round(debt_payments / income * 100, 1) if income > 0 else 0.0


def utilization(limit: float, used: float) -> float:
    return round(min(used / limit * 100, 100), 1) if limit > 0 else 0.0


def category(score: int) -> str:
    if score >= 750:
        return "Excellent"
    if score >= 700:
        return "Good"
    if score >= 600:
        return "Fair"
    return "Poor"


def bottlenecks(r: FinancialRecord) -> list[dict]:
    out = []
    if r.utilization > 30:
        out.append({"title": "High credit utilization",
                    "detail": f"You use {r.utilization}% of your limit. Lenders like it under 30%."})
    if r.missed_payments > 0:
        out.append({"title": "Missed payments",
                    "detail": f"{r.missed_payments} missed payment(s). Payment history is the biggest score factor."})
    if r.debt_to_income > 40:
        out.append({"title": "High debt-to-income ratio",
                    "detail": f"EMIs take {r.debt_to_income}% of income. Aim for under 40%."})
    if r.monthly_expenses + r.monthly_debt_payments > r.monthly_income:
        out.append({"title": "Spending exceeds income",
                    "detail": "Expenses plus EMIs are higher than your monthly income."})
    return out


def dashboard(name: str, records: list[FinancialRecord]) -> dict:
    if not records:
        return {"name": name, "latest": None, "history": []}
    latest = records[-1]
    prev = records[-2] if len(records) > 1 else None
    return {
        "name": name,
        "latest": {
            "credit_score": latest.credit_score,
            "category": category(latest.credit_score),
            "debt_to_income": latest.debt_to_income,
            "utilization": latest.utilization,
            "missed_payments": latest.missed_payments,
            "improvement": latest.credit_score - prev.credit_score if prev else None,
            "points_to_excellent": max(0, 750 - latest.credit_score),
        },
        "bottlenecks": bottlenecks(latest),
        "history": [{"date": r.created_at.strftime("%d %b %Y"), "score": r.credit_score} for r in records],
        "utilization_pie": [
            {"name": "Used", "value": round(latest.credit_used)},
            {"name": "Available", "value": round(max(latest.credit_limit - latest.credit_used, 0))},
        ],
    }
