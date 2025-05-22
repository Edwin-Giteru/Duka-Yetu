from pydantic import BaseModel, EmailStr, Field

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int
    subtotal: float = Field(..., example= 100.98)


class OrderItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    subtotal: float

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "product_id": 1,
                "quantity": 2,
                "subtotal": 39.98
            }
        }