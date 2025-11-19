# app/services/rag_service.py
from openai import OpenAI
from app.config import settings
from app.database import supabase
from typing import List, Dict, Optional

# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def search_cars_with_filters(
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    fuel_type: Optional[str] = None,
    transmission: Optional[str] = None,
    min_seats: Optional[int] = None,
    color: Optional[str] = None,
    brand: Optional[str] = None
) -> List[Dict]:
    """
    Search cars in database with filters
    
    This is the "Retrieval" part of RAG - we retrieve relevant data from our database
    """
    try:
        # Start query
        query = supabase.table("cars").select("*")
        
        # Apply filters
        if min_price is not None:
            query = query.gte("price", min_price)
        if max_price is not None:
            query = query.lte("price", max_price)
        if fuel_type:
            query = query.eq("fuel_type", fuel_type)
        if transmission:
            query = query.eq("transmission", transmission)
        if min_seats is not None:
            query = query.gte("seats", min_seats)
        if color:
            query = query.ilike("color", f"%{color}%")
        if brand:
            query = query.ilike("brand", f"%{brand}%")
        
        # Execute and return
        response = query.execute()
        return response.data
        
    except Exception as e:
        print(f"Error searching cars: {str(e)}")
        return []

def generate_response_with_cars(
    user_message: str, 
    cars: List[Dict], 
    filters: Dict,
    should_suggest_comparison: bool,
    conversation_history: Optional[List[Dict]] = None
) -> str:
    """
    Generate a natural language response using OpenAI with the found cars and conversation history
    """
    try:
        # Prepare context about the cars found
        if not cars:
            cars_context = "No cars found matching the criteria."
        else:
            cars_context = f"Found {len(cars)} car(s):\n\n"
            for i, car in enumerate(cars[:5], 1):
                cars_context += f"{i}. {car['brand']} {car['model']} ({car['year']})\n"
                cars_context += f"   - Price: €{car['price']:,.0f}\n"
                cars_context += f"   - Fuel: {car['fuel_type']}, Transmission: {car['transmission']}\n"
                cars_context += f"   - Seats: {car['seats']}, Doors: {car['doors']}\n"
                cars_context += f"   - Color: {car['color']}\n\n"
        
        # Add comparison suggestion if appropriate
        comparison_instruction = ""
        if should_suggest_comparison and len(cars) >= 2:
            comparison_instruction = "\n\nIMPORTANT: End your response by asking if the user would like to compare these models in a detailed comparison table."
        
        system_prompt = f"""
You are a friendly and knowledgeable car advisor assistant. 
Your job is to help users find the perfect car based on their needs.

IMPORTANT: When answering questions about the cars, ALWAYS refer to the CURRENT CAR DATA provided below, not previous data from the conversation history.

Based on the cars found in the database, provide a helpful, natural response to the user.
- Be conversational and friendly
- Highlight the best matches first
- Mention key features that match their criteria
- If no cars match, suggest adjusting their criteria
- Keep responses concise but informative
- When comparing or ranking cars, use the exact data provided below
{comparison_instruction}
"""
        
        # Build messages array
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history if provided (WITHOUT car data in history)
        if conversation_history:
            # Filter out any old car data from history to avoid confusion
            clean_history = []
            for msg in conversation_history:
                # Only keep the actual user messages and AI responses, not the internal context
                if msg.get("role") in ["user", "assistant"]:
                    clean_history.append(msg)
            messages.extend(clean_history)
        
        # Add CURRENT context with car data (this should take priority)
        current_context = f"""
CURRENT CAR DATA (Use this data to answer the user's question):
{cars_context}

User's current message: {user_message}

Applied filters: {filters}

Please provide a helpful response based on the CURRENT CAR DATA above.
"""
        
        messages.append({"role": "user", "content": current_context})
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error generating response: {str(e)}")
        return "I'm sorry, I encountered an error. Please try again."

def detect_user_satisfaction(user_message: str) -> bool:
    """
    Detect if the user is satisfied and ready to compare cars
    
    Returns True if user seems satisfied (e.g., "perfect", "thanks", "I'll think about it")
    """
    satisfaction_keywords = [
        "perfect", "great", "thanks", "thank you", "looks good", 
        "i'll think", "i will think", "let me think", "appreciate",
        "parfait", "merci", "super", "génial", "je vais réfléchir"
    ]
    
    message_lower = user_message.lower()
    return any(keyword in message_lower for keyword in satisfaction_keywords)

def combine_filters(active_filters: Dict, extracted_filters: Dict) -> Dict:
    """
    Combine manual filters (active_filters) with AI-extracted filters
    
    Manual filters have priority - they are ALWAYS respected
    """
    # Start with active filters (manual)
    combined = dict(active_filters)
    
    # Add extracted filters only if not already set manually
    for key, value in extracted_filters.items():
        if key not in combined or combined[key] is None:
            combined[key] = value
    
    return combined

def get_priority_columns(filters: Dict) -> List[str]:
    """
    Get the columns that should be highlighted in comparison table
    Based on what the user discussed/filtered
    """
    priority_columns = ["brand", "model"]  # Always show these first
    
    # Add columns based on filters used
    filter_to_column = {
        "min_price": "price",
        "max_price": "price",
        "fuel_type": "fuel_type",
        "transmission": "transmission",
        "min_seats": "seats",
        "color": "color"
    }
    
    for filter_key, column_name in filter_to_column.items():
        if filter_key in filters and filters[filter_key] is not None:
            if column_name not in priority_columns:
                priority_columns.append(column_name)
    
    # Add remaining columns
    all_columns = ["year", "doors", "created_at", "updated_at"]
    for col in all_columns:
        if col not in priority_columns:
            priority_columns.append(col)
    
    return priority_columns

def generate_response_with_cars(
    user_message: str, 
    cars: List[Dict], 
    filters: Dict,
    should_suggest_comparison: bool,
    conversation_history: Optional[List[Dict]] = None  # ← VÉRIFIE QUE C'EST ICI
) -> str:
    """
    Generate a natural language response using OpenAI with the found cars and conversation history
    """
    try:
        # Prepare context about the cars found
        if not cars:
            cars_context = "No cars found matching the criteria."
        else:
            cars_context = f"Found {len(cars)} car(s):\n\n"
            for i, car in enumerate(cars[:5], 1):
                cars_context += f"{i}. {car['brand']} {car['model']} ({car['year']})\n"
                cars_context += f"   - Price: €{car['price']:,.0f}\n"
                cars_context += f"   - Fuel: {car['fuel_type']}, Transmission: {car['transmission']}\n"
                cars_context += f"   - Seats: {car['seats']}, Doors: {car['doors']}\n"
                cars_context += f"   - Color: {car['color']}\n\n"
        
        # Add comparison suggestion if appropriate
        comparison_instruction = ""
        if should_suggest_comparison and len(cars) >= 2:
            comparison_instruction = "\n\nIMPORTANT: End your response by asking if the user would like to compare these models in a detailed comparison table."
        
        system_prompt = f"""
You are a friendly and knowledgeable car advisor assistant. 
Your job is to help users find the perfect car based on their needs.

IMPORTANT: When answering questions about the cars, ALWAYS refer to the CURRENT CAR DATA provided below, not previous data from the conversation history.

Based on the cars found in the database, provide a helpful, natural response to the user.
- Be conversational and friendly
- Highlight the best matches first
- Mention key features that match their criteria
- If no cars match, suggest adjusting their criteria
- Keep responses concise but informative
- When comparing or ranking cars, use the exact data provided below
{comparison_instruction}
"""
        
        # Build messages array
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history if provided
        if conversation_history:
            clean_history = []
            for msg in conversation_history:
                if msg.get("role") in ["user", "assistant"]:
                    clean_history.append(msg)
            messages.extend(clean_history)
        
        # Add CURRENT context with car data
        current_context = f"""
CURRENT CAR DATA (Use this data to answer the user's question):
{cars_context}

User's current message: {user_message}

Applied filters: {filters}

Please provide a helpful response based on the CURRENT CAR DATA above.
"""
        
        messages.append({"role": "user", "content": current_context})
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error generating response: {str(e)}")
        return "I'm sorry, I encountered an error. Please try again."


def extract_filters_from_message(
    user_message: str,
    conversation_history: Optional[List[Dict]] = None
) -> Dict:
    """
    Use OpenAI to extract search criteria from user message with conversation context
    """
    try:
        system_prompt = """
You are a car advisor assistant. Extract search filters from the user's message.

IMPORTANT RULES:
1. Only extract filters when the user is REQUESTING to see/find/show cars with specific criteria
2. DO NOT extract filters when the user is asking QUESTIONS about already shown cars
3. Questions like "what color is it?", "how much does it cost?", "tell me more" are NOT filter requests

Consider the conversation history to understand the context.
- If the user refers to "these cars" or "which one", look at the previous filters
- Maintain filters from previous messages unless the user explicitly changes them

Return ONLY a JSON object with these possible keys (all optional):
- min_price (number)
- max_price (number)
- fuel_type (string: "petrol", "diesel", "electric", "hybrid", "plug_in_hybrid")
- transmission (string: "manual", "automatic")
- min_seats (number: 2-9)
- color (string)
- brand (string)

If the user doesn't mention a filter, don't include it in the JSON.

Examples:
User: "I want an electric car under 35000"
Response: {"fuel_type": "electric", "max_price": 35000}

User: "Show me cars under 20000"
Response: {"max_price": 20000}

User (after previous message): "Which one is the cheapest?"
Response: {"max_price": 20000}

User: "What color is it?"
Response: {}

User: "Show me red cars"
Response: {"color": "red"}

User: "Hello, I'm looking for a car"
Response: {}
"""
        
        # Build messages with history for context
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add recent conversation history for context (last 4 messages)
        if conversation_history:
            recent_history = conversation_history[-4:] if len(conversation_history) > 4 else conversation_history
            messages.extend(recent_history)
        
        # Add current message
        messages.append({"role": "user", "content": user_message})
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        # Parse the JSON response
        import json
        filters = json.loads(response.choices[0].message.content)
        return filters
        
    except Exception as e:
        print(f"Error extracting filters: {str(e)}")
        return {}


async def process_chat_message(
    user_message: str,
    active_filters: Optional[Dict] = None,
    conversation_history: Optional[List[Dict]] = None
) -> Dict:
    """
    Main function to process a chat message using RAG with conversation history
    """
    # Default to empty dict if no active filters
    if active_filters is None:
        active_filters = {}
    
    # Step 1: Extract filters using AI WITH HISTORY
    extracted_filters = extract_filters_from_message(
        user_message,
        conversation_history  # ← VÉRIFIE QUE C'EST BIEN ICI
    )
    
    # Step 2: Combine filters (manual filters have priority)
    combined_filters = combine_filters(active_filters, extracted_filters)
    
    # Step 3: Search for cars with combined filters
    cars = search_cars_with_filters(
        min_price=combined_filters.get("min_price"),
        max_price=combined_filters.get("max_price"),
        fuel_type=combined_filters.get("fuel_type"),
        transmission=combined_filters.get("transmission"),
        min_seats=combined_filters.get("min_seats"),
        color=combined_filters.get("color"),
        brand=combined_filters.get("brand")
    )
    
    # Step 4: Detect if user is satisfied (for comparison suggestion)
    should_suggest_comparison = detect_user_satisfaction(user_message)
    
    # Step 5: Generate response WITH HISTORY
    response_text = generate_response_with_cars(
        user_message, 
        cars, 
        combined_filters,
        should_suggest_comparison,
        conversation_history  # ← ET ICI AUSSI
    )
    
    # Step 6: Get priority columns for comparison table
    priority_columns = get_priority_columns(combined_filters)
    
    return {
        "message": response_text,
        "active_filters": active_filters,
        "extracted_filters": extracted_filters,
        "filters_applied": combined_filters,
        "cars_found": len(cars),
        "cars": cars[:5],
        "suggest_comparison": should_suggest_comparison and len(cars) >= 2,
        "priority_columns": priority_columns
    }