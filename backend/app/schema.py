from click import Option
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import List, Annotated, Dict, Any, Optional

class FeedbackCreate(BaseModel):
    user_id: int
    order_id:Optional[int] = None
    product_id: Optional[int]
    ratings: int = Field(..., ge=1, le=5, description="Rating between 1 and 5")
    message: Optional[str] = None

class FeedbackOut(BaseModel):
    id: int
    user_id: int
    order_id: int
    product_id: int
    ratings: int
    message: Optional[str] = None
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

class PaymentRequest(BaseModel):
    order_id: int
    amount: Annotated[float, Field(gt=0, le=500000, description="Payment amount in KES")]
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v: float) -> float:
        """Validate payment amount constraints"""
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        if v > 70000:  # M-Pesa transaction limit
            raise ValueError('Amount exceeds M-Pesa transaction limit (KES 70,000)')
        return round(v, 2)

# Alternative approach using Field constraints (Pydantic v2)
class PaymentRequestSimple(BaseModel):
    order_id: int
    amount: Annotated[float, Field(
        gt=0, 
        le=70000,
        description="Payment amount in KES (1-70000)",
        examples=[100.50, 1500.00]
    )]
    
    # Pydantic v2 automatically rounds and validates based on Field constraints

class PaymentResponse(BaseModel):
    success: bool
    message: str
    checkout_request_id: Optional[str] = None
    merchant_request_id: Optional[str] = None

class CallbackData(BaseModel):
    Body: Dict[Any, Any]

class ProductBase(BaseModel):
    name: str = Field(..., example="Laptop")
    description: Optional[str] = Field(None, example="A high-end gaming laptop")
    price: float = Field(..., gt=0, example=999.99)
    quantity: int = Field(..., ge=0, example=10)    
    category_id: Optional[int] = Field(None, example=1)
    image_url: str = Field(..., example="https://vikombe.com/images")


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, example="Laptop")
    description: Optional[str] = Field(None, example="A high-end gaming laptop")
    price: Optional[float] = Field(None, gt=0, example=999.99)
    in_stock: Optional[int] = Field(None, ge=0, example=10)
    category_id: Optional[int] = Field(None, example=1)
    image_url: Optional[str] = Field(..., example="https://vikombe.com/images")
    
class ProductOut(BaseModel):
    id: int
    name: str = Field(..., example="Laptop")
    description: Optional[str] = Field(None, example="A high-end gaming laptop")
    price: float = Field(..., gt=0, example=999.99)
    stock: int = Field(..., ge=0, example=10)
    image_url: str = Field(..., example="https://vikombe.com/images")    
    

class Product(ProductBase):
    id: int

    class Config:
        from_attributes= True

class UserCreate(BaseModel):
    email: EmailStr = Field(..., example="")
    password: str = Field(..., example="")
    hostel_block: str = Field(..., alias="hostel-block", example="")
    room_number: str = Field(..., alias="room-number", example="")
    phone_number:str =  Field(..., alias="phone-number", example="")
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
    phone_number: str
    is_outside_campus: bool
    created_at: Optional[datetime] = None
    
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    hostel_block: Optional[str] = None
    room_number: Optional[str] = None
    is_outside_campus: Optional[bool] = None  
    phone_number: Optional[str] = None  

    class Config:
        from_attributes = True