from pydantic import BaseModel, EmailStr

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int


class OrderItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    subtotal: float

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "product_id": 1,
                "quantity": 2,
                "subtotal": 39.98
            }
        }