# app/config.py
import os
from typing import List

class Settings:
    """Application settings loaded from environment variables"""
    
    # Supabase Configuration
    SUPABASE_URL: str = os.environ.get("SUPABASE_URL", "")
    SUPABASE_SERVICE_KEY: str = os.environ.get("SUPABASE_SERVICE_KEY", "")
    SUPABASE_ANON_KEY: str = os.environ.get("SUPABASE_ANON_KEY", "")  # Keep for fallback
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
    
    # FastAPI Configuration
    API_HOST: str = os.environ.get("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.environ.get("API_PORT", "8000"))
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "https://lovable.dev",
        "https://1dbbe1bb-01c6-4e10-853b-0c1fc130e9db.lovableproject.com"
        "https://id-preview--1dbbe1bb-01c6-4e10-853b-0c1fc130e9db.lovable.app", 
        "*"
    ]

# Create settings instance
settings = Settings()

# Validate that required settings are present
def validate_settings():
    """Validate that all required environment variables are set"""
    
    # Use SERVICE_KEY if available, otherwise ANON_KEY
    supabase_key = settings.SUPABASE_SERVICE_KEY or settings.SUPABASE_ANON_KEY
    
    required_vars = {
        "SUPABASE_URL": settings.SUPABASE_URL,
        "SUPABASE_KEY": supabase_key,
        "OPENAI_API_KEY": settings.OPENAI_API_KEY,
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    
    if missing_vars:
        print("=" * 50)
        print("🔍 ALL ENVIRONMENT VARIABLES:")
        for key, value in os.environ.items():
            if len(value) > 20:
                print(f"  {key} = {value[:20]}...")
            else:
                print(f"  {key} = {value}")
        print("=" * 50)
        print(f"📊 Settings values loaded:")
        print(f"  SUPABASE_URL = {settings.SUPABASE_URL[:30] if settings.SUPABASE_URL else 'EMPTY'}...")
        print(f"  SUPABASE_SERVICE_KEY = {settings.SUPABASE_SERVICE_KEY[:30] if settings.SUPABASE_SERVICE_KEY else 'EMPTY'}...")
        print(f"  SUPABASE_ANON_KEY = {settings.SUPABASE_ANON_KEY[:30] if settings.SUPABASE_ANON_KEY else 'EMPTY'}...")
        print(f"  OPENAI_API_KEY = {settings.OPENAI_API_KEY[:20] if settings.OPENAI_API_KEY else 'EMPTY'}...")
        
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )
    
    print("✅ All configuration settings loaded successfully!")
    print(f"🔑 Using {'SERVICE_KEY' if settings.SUPABASE_SERVICE_KEY else 'ANON_KEY'}")