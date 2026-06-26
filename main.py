import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

import models
from database import engine, Base
from routers import expenses, chat, goals, income, budgets

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Expense Tracker",
    description="A smart expense tracker powered by Gemini",
    version="1.0.0"
)

# Ensure static and template directories exist (for local testing without them failing)
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Include Routers
app.include_router(expenses.router)
app.include_router(chat.router)
app.include_router(goals.router)
app.include_router(income.router)
app.include_router(budgets.router)

# Serve the frontend
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
