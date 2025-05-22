from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class OrderItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    price_per_item: float
    subtotal: float

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    user_id: int = Field(..., example=1)
    total_price: float = Field(..., example=100.99)
    delivery_address: str = Field(..., example="CBD Bogoria 3")
    payment_status: str = Field(..., example="Pending") 
    order_items: List[OrderItemOut] 

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    total_price: Optional[float] = Field(None, example=100.99)
    delivery_address: Optional[str] = Field(None, example="CBD Bogoria 3")
    payment_status: Optional[str] = Field(None, example="Completed")

class OrderOut(OrderBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True