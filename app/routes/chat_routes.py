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
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "I want an electric family car",
                "active_filters": {
                    "max_price": 40000,
                    "fuel_type": "electric"
                }
            }
        }

# Response model
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
    Chat with the AI car advisor
    
    This endpoint processes user messages using RAG (Retrieval Augmented Generation):
    1. Extracts filters from the message using AI
    2. Combines with active manual filters
    3. Searches for matching cars in the database
    4. Generates a natural language response
    5. Suggests comparison if user seems satisfied
    
    **Example request:**
```json
    {
        "message": "I need a family car with good fuel economy",
        "active_filters": {
            "max_price": 30000
        }
    }
```
    """
    try:
        # Process the message using RAG
        result = await process_chat_message(
            user_message=request.message,
            active_filters=request.active_filters
        )
        
        return result
        
    except Exception as e:
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