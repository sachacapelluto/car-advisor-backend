# app/models/car.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

# Enums for validated choices
class FuelType(str, Enum):
    """Valid fuel types"""
    petrol = "petrol"
    diesel = "diesel"
    electric = "electric"
    hybrid = "hybrid"
    plug_in_hybrid = "plug_in_hybrid"

class TransmissionType(str, Enum):
    """Valid transmission types"""
    manual = "manual"
    automatic = "automatic"

# Base model for Car (shared fields)
class CarBase(BaseModel):
    """Base car model with common fields"""
    brand: str = Field(..., min_length=1, max_length=100, description="Car brand")
    model: str = Field(..., min_length=1, max_length=100, description="Car model")
    year: int = Field(..., ge=1900, le=2030, description="Year of manufacture")
    price: float = Field(..., ge=0, description="Price in euros")
    fuel_type: FuelType = Field(..., description="Type of fuel")
    transmission: TransmissionType = Field(..., description="Type of transmission")
    seats: int = Field(..., ge=2, le=9, description="Number of seats")
    doors: int = Field(..., ge=2, le=5, description="Number of doors")
    color: str = Field(..., min_length=1, max_length=50, description="Color")

# Model for creating a car (no id, timestamps)
class CarCreate(CarBase):
    """Model for creating a new car"""
    pass

# Model for updating a car (all fields optional)
class CarUpdate(BaseModel):
    """Model for updating an existing car"""
    brand: Optional[str] = Field(None, min_length=1, max_length=100)
    model: Optional[str] = Field(None, min_length=1, max_length=100)
    year: Optional[int] = Field(None, ge=1900, le=2030)
    price: Optional[float] = Field(None, ge=0)
    fuel_type: Optional[FuelType] = None
    transmission: Optional[TransmissionType] = None
    seats: Optional[int] = Field(None, ge=2, le=9)
    doors: Optional[int] = Field(None, ge=2, le=5)
    color: Optional[str] = Field(None, min_length=1, max_length=50)

# Model for reading a car (includes id and timestamps)
class Car(CarBase):
    """Model for reading a car from database"""
    id: str = Field(..., description="Unique identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True  # Allows creating from SQLAlchemy models

# Model for car filters
class CarFilters(BaseModel):
    """Model for filtering cars"""
    brand: Optional[str] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    fuel_type: Optional[FuelType] = None
    transmission: Optional[TransmissionType] = None
    min_seats: Optional[int] = Field(None, ge=2, le=9)
    color: Optional[str] = None
    min_year: Optional[int] = Field(None, ge=1900, le=2030)
    max_year: Optional[int] = Field(None, ge=1900, le=2030)