from pydantic import BaseModel, Field
from typing import Optional

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
    image_url: Optional[str] = Field(None, example="https://vikombe.com/images")
    
class ProductOut(ProductBase):
    pass

class Product(ProductBase):
    id: int

    class Config:
        from_attributes= True