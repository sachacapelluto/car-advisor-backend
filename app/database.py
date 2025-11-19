# app/database.py
from supabase import create_client, Client
from app.config import settings

def get_supabase_client() -> Client:
    """Create and return a Supabase client"""
    # Prioritize service_role key for backend operations
    supabase_key = settings.SUPABASE_SERVICE_KEY if settings.SUPABASE_SERVICE_KEY else settings.SUPABASE_ANON_KEY
    
    if not settings.SUPABASE_URL or not supabase_key:
        raise ValueError("Supabase credentials not configured")
    
    print(f"🔑 Using Supabase key type: {'SERVICE_ROLE' if settings.SUPABASE_SERVICE_KEY else 'ANON'}")
    
    return create_client(
        supabase_url=settings.SUPABASE_URL,
        supabase_key=supabase_key
    )

# Create the client
supabase: Client = get_supabase_client()