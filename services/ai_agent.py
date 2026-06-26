import os
import google.generativeai as genai
from sqlalchemy.orm import Session
from database import SessionLocal
import models
from services import expense_service
from datetime import date
import json

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# Define the tools (functions) the model can use

def add_expense_tool(amount: float, category: str, description: str, expense_date: str = None) -> str:
    """
    Adds a new expense to the database. Use this when the user mentions they spent money.
    Args:
        amount: The monetary value of the expense (e.g., 20.5)
        category: The category of the expense (e.g., 'Food', 'Transport', 'Entertainment', 'Utilities', 'Shopping', 'Other')
        description: A short description of the expense.
        expense_date: The date in YYYY-MM-DD format. If not provided, use today's date.
    """
    if not expense_date:
        expense_date = date.today().isoformat()
        
    db = SessionLocal()
    try:
        new_expense = models.ExpenseCreate(
            amount=amount,
            category=category,
            description=description,
            date=date.fromisoformat(expense_date)
        )
        expense_service.create_expense(db, new_expense)
        return f"Successfully added expense: {amount} for {category} on {expense_date}."
    except Exception as e:
        return f"Failed to add expense: {str(e)}"
    finally:
        db.close()

def get_expense_summary_tool() -> str:
    """
    Retrieves the total expenses and a breakdown by category from the database.
    Use this when the user asks about their spending, total expenses, or wants an analysis of their spending.
    """
    db = SessionLocal()
    try:
        summary = expense_service.get_expense_summary(db)
        return json.dumps(summary)
    except Exception as e:
        return f"Failed to get summary: {str(e)}"
    finally:
        db.close()

def get_recent_expenses_tool(limit: int = 50) -> str:
    """
    Retrieves the raw line-by-line recent expenses from the database.
    Use this when the user asks about specific days, individual transactions, or "how much did I spend on X day".
    """
    db = SessionLocal()
    try:
        from services import expense_service
        expenses = expense_service.get_expenses(db, limit=limit)
        return json.dumps([{"date": str(e.date), "category": e.category, "amount": e.amount, "desc": e.description} for e in expenses])
    except Exception as e:
        return f"Failed to get recent expenses: {str(e)}"
    finally:
        db.close()

def get_goals_tool() -> str:
    """
    Retrieves the user's current spending/saving goals and their progress.
    """
    db = SessionLocal()
    try:
        from services import goal_service
        goals = goal_service.get_goals(db)
        return json.dumps([{"name": g.name, "target": g.target_amount, "current": g.current_amount, "deadline": str(g.deadline)} for g in goals])
    except Exception as e:
        return f"Failed to get goals: {str(e)}"
    finally:
        db.close()

def get_budget_limits_tool() -> str:
    """
    Retrieves the user's monthly budget limits for categories.
    """
    db = SessionLocal()
    try:
        from services import budget_service
        limits = budget_service.get_budget_limits(db)
        return json.dumps([{"category": b.category, "limit": b.amount} for b in limits])
    except Exception as e:
        return f"Failed to get budget limits: {str(e)}"
    finally:
        db.close()

def get_expenses_by_month_tool(year: int, month: int) -> str:
    """
    Retrieves the total expenses and breakdown by category for a specific past month and year.
    Use this when the user asks about spending or expenses for a specific past month (e.g., February 2026).
    Args:
        year: The year (e.g., 2026)
        month: The month as an integer (1 for January, 2 for February, etc.)
    """
    db = SessionLocal()
    try:
        from services import expense_service
        summary = expense_service.get_expense_summary_by_month(db, year, month)
        return json.dumps(summary)
    except Exception as e:
        return f"Failed to get summary for {month}/{year}: {str(e)}"
    finally:
        db.close()

def get_yearly_expense_summary_tool(year: int) -> str:
    """
    Retrieves the total expenses and breakdown by category for each month of a specific year.
    Use this when the user asks questions comparing months, finding the max/min spending month, or asking about spending across an entire year.
    Args:
        year: The year (e.g., 2026)
    """
    db = SessionLocal()
    try:
        from services import expense_service
        summary = expense_service.get_yearly_expense_summary(db, year)
        return json.dumps(summary)
    except Exception as e:
        return f"Failed to get yearly summary for {year}: {str(e)}"
    finally:
        db.close()

# System instruction for the agent
SYSTEM_INSTRUCTION = """
You are a highly intelligent, friendly, and helpful Financial Assistant.
You help the user manage their expenses and provide financial insights.

You have access to tools that allow you to:
1. Add an expense (`add_expense_tool`).
2. Get summary of spending (`get_expense_summary_tool`).
3. Get line-by-line detailed expenses (`get_recent_expenses_tool`).
4. Check goals progress (`get_goals_tool`).
5. Check budget limits (`get_budget_limits_tool`).
6. Get past month expense summary (`get_expenses_by_month_tool`).
7. Get yearly expense summary broken down by month (`get_yearly_expense_summary_tool`).

When a user says they spent money, ALWAYS use the `add_expense_tool` to log it. 
If they ask for details on specific days, use `get_recent_expenses_tool`.
If they ask about goals or budgets, check those tools to provide accurate advice and progress percentages.
If they ask about past months or specific dates, use `get_expenses_by_month_tool` or `get_recent_expenses_tool`.
If they ask to compare months, find max spending month, or analyze a full year, use `get_yearly_expense_summary_tool`.
Always format your response using Markdown. The currency is now INR (₹).
"""

# Initialize model with tools
def get_chat_session():
    if not os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY") == "your_gemini_api_key_here":
         return None # Or raise an error
         
    model = genai.GenerativeModel(
        model_name="gemini-flash-latest",
        system_instruction=SYSTEM_INSTRUCTION,
        tools=[
            add_expense_tool, 
            get_expense_summary_tool,
            get_recent_expenses_tool,
            get_goals_tool,
            get_budget_limits_tool,
            get_expenses_by_month_tool,
            get_yearly_expense_summary_tool
        ]
    )
    # Start a chat session with automatic function calling enabled
    chat = model.start_chat(enable_automatic_function_calling=True)
    return chat

# Global chat session to maintain some memory (in a real app, this would be tied to user session)
_global_chat = None

def process_chat_message(message: str) -> str:
    global _global_chat
    
    # Lazy initialization
    if _global_chat is None:
        _global_chat = get_chat_session()
        
    if _global_chat is None:
        return "Error: Gemini API key is not configured properly in the .env file."
        
    try:
        response = _global_chat.send_message(message)
        return response.text
    except Exception as e:
        return f"An error occurred while communicating with the AI: {str(e)}"

def categorize_expense_with_ai(description: str) -> str:
    if not description:
        return "Other"
        
    prompt = f"Categorize the following expense description into exactly ONE of these categories: Food, Transport, Shopping, Utilities, Entertainment, Other. Reply with ONLY the category word, nothing else.\n\nDescription: {description}"
    try:
        model = genai.GenerativeModel("gemini-flash-latest")
        response = model.generate_content(prompt)
        cat = response.text.strip().title()
        valid_categories = ["Food", "Transport", "Shopping", "Utilities", "Entertainment", "Other"]
        if cat in valid_categories:
            return cat
        
        # Fuzzy match just in case
        for valid in valid_categories:
            if valid.lower() in cat.lower():
                return valid
                
        return "Other"
    except Exception:
        return "Other"
