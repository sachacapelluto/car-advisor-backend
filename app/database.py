# app/database.py
from supabase import create_client, Client
from app.config import settings

def get_supabase_client() -> Client:
    """Create and return a Supabase client"""
    # Use SERVICE_KEY (preferred) or ANON_KEY as fallback
    supabase_key = settings.SUPABASE_SERVICE_KEY or settings.SUPABASE_ANON_KEY
    
    if not settings.SUPABASE_URL or not supabase_key:
        raise ValueError("Supabase credentials not configured")
    
    return create_client(
        supabase_url=settings.SUPABASE_URL,
        supabase_key=supabase_key
    )

# Create the client
supabase: Client = get_supabase_client()