# app/database.py
from supabase import create_client, Client
from app.config import settings

def get_supabase_client() -> Client:
    """Create and return a Supabase client"""
    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
        raise ValueError("Supabase credentials not configured")
    
    return create_client(
        supabase_url=settings.SUPABASE_URL,
        supabase_key=settings.SUPABASE_ANON_KEY
    )

# Create the client
supabase: Client = get_supabase_client()