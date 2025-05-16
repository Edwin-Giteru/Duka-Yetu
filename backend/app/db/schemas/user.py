from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    hostel_block: str
    room_number: str
    role: str
    is_outside_campus: bool
    full_name: str
    created_at: Optional[datetime] = None


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