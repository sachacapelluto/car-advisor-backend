# app/database.py
from supabase import create_client, Client
from app.config import settings

# Create Supabase client instance
supabase: Client = create_client(
    supabase_url=settings.SUPABASE_URL,
    supabase_key=settings.SUPABASE_SERVICE_KEY
)

def get_supabase_client() -> Client:
    """
    Returns the Supabase client instance.
    This function can be used as a dependency in FastAPI routes.
    """
    return supabase

# Test connection function
async def test_connection():
    """Test if the connection to Supabase is working"""
    try:
        # Try to fetch one car from the database
        response = supabase.table("cars").select("*").limit(1).execute()
        print(f"✅ Database connection successful! Found {len(response.data)} test record(s)")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False