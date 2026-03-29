from fastapi import FastAPI
from pydantic import BaseModel
from decimal import Decimal
from db import get_connection
from llm_parser import extract_transaction
import requests
from datetime import datetime

app = FastAPI()


class ExpenseRequest(BaseModel):
    user_id: int
    amount: Decimal   # ✅ Use Decimal instead of float
    category: str
    description: str

@app.post("/add_expense")
def add_expense(expense: ExpenseRequest):

    conn = get_connection()
    cursor = conn.cursor()

    try:
        insert_query = """
        INSERT INTO expenses (user_id, amount, category, description)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            expense.user_id,
            expense.amount,
            expense.category,
            expense.description
        ))
        conn.commit()

        expense_sum_query = """
        SELECT COALESCE(SUM(amount), 0)
        FROM expenses
        WHERE user_id = %s
        """
        cursor.execute(expense_sum_query, (expense.user_id,))
        total_spent = cursor.fetchone()[0]

        income_query = """
        SELECT COALESCE(SUM(amount), 0)
        FROM income
        WHERE user_id = %s
        """
        cursor.execute(income_query, (expense.user_id,))
        total_income = cursor.fetchone()[0]

        warning = None

        if total_income > 0 and total_spent > Decimal("0.8") * total_income:
            warning = "⚠️ Overspending: You have used more than 80% of your income!"
                
        
        current_day = datetime.now().day

        # Avoid division by zero
        daily_avg = total_spent / current_day

        # Next 7-day trajectory
        next_7_days_spend = daily_avg * 7

        trajectory_msg = f"📈 At this pace, you may spend around ₹{int(next_7_days_spend)} more in the next 7 days."
        
        remaining_balance = total_income - total_spent

        return {
            "reply": f"✅ Logged ₹{expense.amount} under {expense.category}",
            "total_spent": float(total_spent),
            "remaining": float(remaining_balance),
            "warning": warning,
            "trajectory": trajectory_msg
        }

    finally:
        cursor.close()
        conn.close()

class ChatRequest(BaseModel):
    user_message: str

@app.post("/chat")
def chat(request: ChatRequest):

    user_message = request.user_message
    data = extract_transaction(user_message)

    if data["type"] == "expense":
        return add_expense(ExpenseRequest(
            user_id=1,
            amount=data["amount"],
            category=data["category"],
            description=data["description"]
        ))

    return {
        "reply": "Income logging coming next",
        "remaining": 0,
        "warning": None
    }

