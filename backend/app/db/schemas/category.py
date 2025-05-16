from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="Category name")
    description: str = Field(..., min_length=1, max_length=255, description="Category description")

class CategoryBase(BaseModel):
    name: str
    description: str

class CategoryGet(BaseModel):
    name: str

class CategoryOut(CategoryBase):
    id: int
    name: str
    description: str
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Electronics",
                "description": "Devices and gadgets",
                "created_at": "2023-10-01T12:00:00Z"
            }
        }