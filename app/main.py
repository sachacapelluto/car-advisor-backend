# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings, validate_settings

# Validate settings on startup
validate_settings()

# Create FastAPI app
app = FastAPI(
    title="Car Advisor API",
    description="Backend API for AI-powered car recommendation chatbot with RAG",
    version="1.0.0"
)

# Configure CORS (allows frontend to communicate with backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers AFTER app creation
from app.routes.car_routes import router as car_router
from app.routes.chat_routes import router as chat_router

app.include_router(car_router)
app.include_router(chat_router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Car Advisor API is running!",
        "version": "1.0.0",
        "status": "healthy",
        "features": ["cars", "chat", "rag", "comparison"]
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "database": "connected",
        "ai": "enabled"
    }
