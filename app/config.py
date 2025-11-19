# app/config.py
import os
from typing import List

class Settings:
    """Application settings loaded from environment variables"""
    
    # Supabase Configuration
    SUPABASE_URL: str = os.environ.get("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.environ.get("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_KEY: str = os.environ.get("SUPABASE_SERVICE_KEY", "")
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
    
    # FastAPI Configuration
    API_HOST: str = os.environ.get("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.environ.get("API_PORT", "8000"))
    
    # CORS Configuration (for frontend)
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "https://lovable.dev",
        "*"  # Temporairement, accepte toutes les origines (pour développement)
    ]

# Create settings instance
settings = Settings()

# Validate that required settings are present
def validate_settings():
    """Validate that all required environment variables are set"""
    required_vars = {
        "SUPABASE_URL": settings.SUPABASE_URL,
        "SUPABASE_ANON_KEY": settings.SUPABASE_ANON_KEY,
        "OPENAI_API_KEY": settings.OPENAI_API_KEY,
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    
    if missing_vars:
        # Print all env vars for debugging
        print("🔍 Environment variables available:")
        for key in os.environ.keys():
            if any(x in key for x in ["SUPABASE", "OPENAI", "API"]):
                print(f"  - {key}")
        
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )
    
    print("✅ All configuration settings loaded successfully!")