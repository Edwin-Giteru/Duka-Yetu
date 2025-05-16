from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class FeedbackCreate(BaseModel):
    user_id: int
    order_id: int
    rating: int = Field(..., ge=1, le=5, description="Rating between 1 and 5")
    comment: Optional[str] = None

class FeedbackOut(BaseModel):
    id: int
    user_id: int
    order_id: int
    rating: int
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "order_id": 1,
                "rating": 5,
                "comment": "Great service!",
                "created_at": "2023-10-01T12:00:00Z"
            }
        }