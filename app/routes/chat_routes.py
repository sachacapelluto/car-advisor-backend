# app/routes/chat_routes.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
from app.services.rag_service import process_chat_message

# Create router
router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

# Request model
class ChatRequest(BaseModel):
    """Model for chat request"""
    message: str
    active_filters: Optional[Dict] = None
    conversation_history: Optional[List[Dict]] = []  # ← AJOUT ICI
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "I want an electric family car",
                "active_filters": {
                    "max_price": 40000,
                    "fuel_type": "electric"
                },
                "conversation_history": [  # ← AJOUT ICI
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi! How can I help?"}
                ]
            }
        }

# Response model (inchangé)
class ChatResponse(BaseModel):
    """Model for chat response"""
    message: str
    active_filters: Dict
    extracted_filters: Dict
    filters_applied: Dict
    cars_found: int
    cars: List[Dict]
    suggest_comparison: bool
    priority_columns: List[str]

@router.post("/", response_model=ChatResponse)
async def chat_with_advisor(request: ChatRequest):
    """
    Chat with the AI car advisor with conversation history
    """
    try:
        print("=== DEBUG: Chat request received ===")
        print(f"Message: {request.message}")
        print(f"Active filters: {request.active_filters}")
        print(f"Conversation history length: {len(request.conversation_history) if request.conversation_history else 0}")
        
        # Process the message using RAG with history
        result = await process_chat_message(
            user_message=request.message,
            active_filters=request.active_filters,
            conversation_history=request.conversation_history
        )
        
        print("=== DEBUG: Response generated successfully ===")
        return result
        
    except Exception as e:
        print(f"=== ERROR in chat_with_advisor ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing chat message: {str(e)}"
        )

@router.get("/health")
async def chat_health():
    """Health check for chat service"""
    return {
        "status": "ok",
        "service": "chat",
        "rag_enabled": True
    }