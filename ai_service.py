"""Personalised advice from Google Gemini, with a rule-based fallback."""
import json
import os

from logic import bottlenecks, category
from models import FinancialRecord

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

PROMPT = """You are a credit advisor for users in India (CIBIL / Experian / Equifax scale 300-900).
Analyse this profile and give a 5-step action plan to reach an Excellent score (750+).
Follow Indian banking norms (30% utilization, 40% EMI-to-income, on-time EMIs, avoid many hard enquiries).
Reply ONLY with JSON: {{"summary": "<2 sentences>", "steps": ["<step 1>", ... exactly 5 steps]}}
Use INR. Be specific to the numbers below. Never promise a score outcome.

Profile:
- Credit score: {score} ({cat})
- Monthly income: INR {income:,.0f}
- Monthly expenses: INR {exp:,.0f}
- Monthly EMIs: INR {emi:,.0f} (debt-to-income {dti}%)
- Card utilization: {util}% (INR {used:,.0f} of INR {limit:,.0f})
- Missed payments: {missed}
"""


def fallback(r: FinancialRecord) -> dict:
    steps = []
    if r.missed_payments:
        steps.append("Clear any overdue amounts now and set auto-debit for every EMI and card bill.")
    else:
        steps.append("Keep paying every EMI and card bill on time. Set auto-debit so none is missed.")
    if r.utilization > 30:
        target = r.credit_limit * 0.3
        steps.append(f"Bring card usage under INR {target:,.0f} (30% of your limit) by paying down before the statement date.")
    else:
        steps.append("Keep card usage under 30% of your limit, even when you can pay in full.")
    if r.debt_to_income > 40:
        steps.append("Prepay your smallest or highest-interest loan to bring EMIs below 40% of income.")
    else:
        steps.append("Avoid taking new loans for now so your EMI-to-income ratio stays healthy.")
    steps.append("Do not apply for new cards or loans for 6 months. Each application adds a hard enquiry.")
    steps.append("Keep your oldest card open and check your free credit report every few months for errors.")
    return {"summary": f"Your score is {r.credit_score} ({category(r.credit_score)}). "
                       f"{len(bottlenecks(r))} area(s) are holding it back.",
            "steps": steps[:5], "source": "fallback"}


def get_advice(r: FinancialRecord) -> dict:
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        return fallback(r)
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=key)
        resp = client.models.generate_content(
            model=MODEL,
            contents=PROMPT.format(
                score=r.credit_score, cat=category(r.credit_score), income=r.monthly_income,
                exp=r.monthly_expenses, emi=r.monthly_debt_payments, dti=r.debt_to_income,
                util=r.utilization, used=r.credit_used, limit=r.credit_limit, missed=r.missed_payments),
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        data = json.loads(resp.text)
        steps = [str(s) for s in data["steps"]][:5]
        if len(steps) < 3:
            raise ValueError("too few steps")
        return {"summary": str(data["summary"]), "steps": steps, "source": "gemini"}
    except Exception as e:  # network, quota, bad JSON: still give the user something useful
        print("Gemini failed, using fallback:", repr(e))
        return fallback(r)
