# FinanceAI - Agentic Expense Tracker

FinanceAI is a modern, production-ready, AI-powered financial management dashboard. It goes beyond simple CRUD operations by integrating an **Agentic AI Workflow** powered by Google's Gemini models, allowing users to converse naturally with their finances, automatically categorize spending, and receive smart email alerts.

## 🧩 Tech Stack

### Backend
* **Python 3.13**
* **FastAPI**: High-performance asynchronous web framework for building APIs.
* **SQLAlchemy & SQLite**: ORM and lightweight database for persistent, local storage.
* **smtplib**: Built-in Python library for automated Gmail alerts.

### Frontend
* **Vanilla HTML5, CSS3, & JavaScript**: Zero-build-step frontend for ultimate simplicity and speed.
* **Chart.js**: Dynamic, responsive data visualization.
* **Modern UI/UX**: Custom dark-mode aesthetic with glassmorphism, flexbox/grid layouts, and micro-animations.

### AI Integration
* **Google Gemini API (`gemini-2.5-flash`)**: State-of-the-art LLM used for intelligent routing, function calling, and natural language processing.

---

## 🤖 LLM Integration & Agentic Workflow

This application does not just use the AI as a chatbot; it uses it as an **Autonomous Agent**.

### 1. Function Calling (Tool Use)
The Gemini model is initialized with a system prompt and a suite of Python functions ("tools") that directly interact with the SQLite database. 
* **Available Tools:** `add_expense_tool`, `get_expense_summary_tool`, `get_recent_expenses_tool`, `get_goals_tool`, `get_budget_limits_tool`.
* **Workflow:** When the user types *"I spent ₹500 on an Uber today"*, the AI autonomously parses the intent, extracts the variables (Amount: 500, Category: Transport), and executes the `add_expense_tool` to insert the data directly into the database. If the user asks *"How am I doing on my budgets?"*, the AI calls the database tools, reads the structured JSON output, and formulates a natural language summary.

### 2. Zero-Shot Auto-Categorization
When a user manually logs an expense via the UI, they do not need to select a category. They only provide a description (e.g., "Starbucks"). The backend intercepts the payload, sends the description to Gemini, and asks it to strictly categorize it into one of the predefined categories (Food, Transport, Shopping, Utilities, Entertainment, Other) before saving it to the database.

---

## ✨ Core Features

1. **Intelligent Dashboard**: View total bank balance, monthly income vs. spending, and a dynamic doughnut chart visualizing expenses by category.
2. **Conversational Finance**: A built-in chat window to add expenses naturally or ask complex queries about your financial health.
3. **Savings Goals Tracker**: Set target amounts for specific goals (e.g., "Travel Fund"). Add funds incrementally and watch your progress bar fill up.
4. **Category Budget Limits**: Set strict monthly spending limits for specific categories (e.g., ₹5000 for Food).
5. **Automated Gmail Alerts**: A background asynchronous worker checks your category budgets every time a new expense is logged. If you exceed a limit, it instantly sends an automated warning email to your inbox.
6. **Unified Ledger**: A dedicated Transactions tab showing a chronological history of both incomes and expenses.

---

## 🚀 How to Run the App

Follow these steps to set up and run the app on your local machine:

### Step 1: Create the Environment Variables
In the root directory of the project, create a new file named `.env`. Add the following credentials to it:

```env
# Database
DATABASE_URL=sqlite:///./expenses.db

# Gemini AI (Get an API key from Google AI Studio)
GEMINI_API_KEY=your_gemini_api_key_here

# Gmail Alerts Setup
# Note: You must use a 16-digit Google "App Password", NOT your standard login password.
USER_EMAIL=your.email@gmail.com
GMAIL_APP_PASSWORD=your_16_digit_app_password
```

### Step 2: Install Dependencies
Open your terminal inside the project folder and install the required Python packages:
```bash
pip install -r requirements.txt
```

### Step 3: Run the Server
Start the FastAPI server using Uvicorn:
```bash
uvicorn main:app --reload
```

### Step 4: Open the App
Once the server is running, open your web browser and navigate to:
**http://127.0.0.1:8000**

---

## ⚡ Quick Start Shortcut (Windows)

You **only** need to complete Steps 1 and 2 the very first time you set up the project. Steps 3 and 4 must be done every time you want to use the app.

To make launching the app effortless, you can create a 1-click startup script:

1. Inside your project folder, create a new file called `Start App.bat`.
2. Open it in a text editor and paste the following code:
```bat
@echo off
start http://127.0.0.1:8000
uvicorn main:app --reload
```
3. Save the file. 

Now, whenever you want to open your AI Expense Tracker, simply double-click **`Start App.bat`**. It will automatically start the backend server and open the web browser for you!

*Enjoy managing your finances with AI!*
