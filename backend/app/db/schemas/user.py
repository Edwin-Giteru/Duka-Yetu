from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr = Field(..., example="")
    password: str = Field(..., example="")
    hostel_block: str = Field(..., alias="hostel-block", example="")
    room_number: str = Field(..., alias="room-number", example="")
    role: str
    is_outside_campus: bool
    full_name: str = Field(..., example=" ")
    created_at: Optional[datetime] = None

    class Config:
        allow_population_by_field_name=True
class UserOut(BaseModel):
    email: EmailStr
    full_name: str
    hostel_block: str
    room_number: str
    role: str
    is_outside_campus: bool
    created_at: Optional[datetime] = None
    
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    hostel_block: Optional[str] = None
    room_number: Optional[str] = None
    is_outside_campus: Optional[bool] = None    

    class Config:
        from_attributes = True