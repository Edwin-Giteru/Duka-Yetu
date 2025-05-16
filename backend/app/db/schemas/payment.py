from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class PaymentCreate(BaseModel):
    order_id: int
    payment_method: str
    amount: float = Field(..., gt=0, description="Amount to be paid")
    status: str = "Pending"  # Default status is 'Pending'
    transaction_id: Optional[str] = None

class PaymentOut(BaseModel):
    id: int
    order_id: int
    payment_method: str
    amount: float
    status: str
    transaction_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "order_id": 1,
                "payment_method": "Credit Card",
                "amount": 39.98,
                "status": "Completed",
                "transaction_id": "txn_1234567890",
                "created_at": "2023-10-01T12:00:00Z"
            }
        }