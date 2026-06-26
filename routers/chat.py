from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import models
from services.ai_agent import process_chat_message

router = APIRouter(
    prefix="/api/chat",
    tags=["chat"]
)

@router.post("/")
def chat_with_agent(request: models.ChatRequest):
    if not request.message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
        
    response_text = process_chat_message(request.message)
    return {"response": response_text}
