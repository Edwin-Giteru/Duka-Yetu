from pydantic import BaseModel, field_validator, Field
from typing import Annotated, Dict, Any, Optional

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
