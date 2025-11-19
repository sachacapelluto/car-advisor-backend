# app/routes/cars.py
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.database import supabase
from app.models.car_model import Car, CarCreate, CarUpdate, CarFilters
from pydantic import BaseModel

# Create router
router = APIRouter(
    prefix="/cars",
    tags=["cars"]
)

@router.get("/", response_model=List[Car])
async def get_cars(
    brand: Optional[str] = Query(None, description="Filter by brand"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    fuel_type: Optional[str] = Query(None, description="Filter by fuel type"),
    transmission: Optional[str] = Query(None, description="Filter by transmission"),
    min_seats: Optional[int] = Query(None, ge=2, le=9, description="Minimum seats"),
    color: Optional[str] = Query(None, description="Filter by color")
):
    """
    Get all cars with optional filters
    
    This endpoint retrieves all cars from the database.
    You can filter by brand, price range, fuel type, transmission, seats, and color.
    """
    try:
        # Start query
        query = supabase.table("cars").select("*")
        
        # Apply filters if provided
        if brand:
            query = query.ilike("brand", f"%{brand}%")
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
        
        # Execute query
        response = query.execute()
        return response.data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching cars: {str(e)}")

@router.get("/{car_id}", response_model=Car)
async def get_car(car_id: str):
    """
    Get a specific car by ID
    
    Returns detailed information about a single car.
    """
    try:
        response = supabase.table("cars").select("*").eq("id", car_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Car not found")
        
        return response.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching car: {str(e)}")

@router.post("/", response_model=Car, status_code=201)
async def create_car(car: CarCreate):
    """
    Create a new car
    
    Add a new car to the database.
    """
    try:
        car_data = car.model_dump()
        response = supabase.table("cars").insert(car_data).execute()
        return response.data[0]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating car: {str(e)}")

@router.put("/{car_id}", response_model=Car)
async def update_car(car_id: str, car: CarUpdate):
    """
    Update an existing car
    
    Update car details. Only provided fields will be updated.
    """
    try:
        # Get only non-None fields
        car_data = car.model_dump(exclude_none=True)
        
        if not car_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        response = supabase.table("cars").update(car_data).eq("id", car_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Car not found")
        
        return response.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating car: {str(e)}")

@router.delete("/{car_id}")
async def delete_car(car_id: str):
    """
    Delete a car
    
    Remove a car from the database.
    """
    try:
        response = supabase.table("cars").delete().eq("id", car_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Car not found")
        
        return {"message": "Car deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting car: {str(e)}")

# Comparison endpoint
class CompareRequest(BaseModel):
    """Model for comparison request"""
    car_ids: List[str]
    priority_columns: Optional[List[str]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "car_ids": [
                    "dbdb1793-c4a9-45ed-9067-9aab890305ba",
                    "550e8400-e29b-41d4-a716-446655440000"
                ],
                "priority_columns": ["brand", "model", "price", "fuel_type"]
            }
        }

@router.post("/compare")
async def compare_cars(request: CompareRequest):
    """
    Compare multiple cars side by side
    
    Returns detailed information for selected cars with priority columns first.
    Priority columns are the ones the user discussed/filtered on.
    """
    try:
        if len(request.car_ids) < 2:
            raise HTTPException(
                status_code=400, 
                detail="At least 2 cars are required for comparison"
            )
        
        if len(request.car_ids) > 5:
            raise HTTPException(
                status_code=400, 
                detail="Maximum 5 cars can be compared at once"
            )
        
        # Fetch all requested cars
        cars = []
        for car_id in request.car_ids:
            response = supabase.table("cars").select("*").eq("id", car_id).execute()
            if response.data:
                cars.append(response.data[0])
        
        if len(cars) != len(request.car_ids):
            raise HTTPException(
                status_code=404,
                detail="Some cars were not found"
            )
        
        return {
            "cars": cars,
            "priority_columns": request.priority_columns or [
                "brand", "model", "price", "fuel_type", 
                "transmission", "seats", "doors", "color", "year"
            ],
            "comparison_count": len(cars)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error comparing cars: {str(e)}"
        )       