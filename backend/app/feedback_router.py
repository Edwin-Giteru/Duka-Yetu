from backend.app.models import Feedback, User, Product, Order
from backend.app.schema import FeedbackCreate, FeedbackOut
from sqlalchemy.orm import Session
from backend.app.dependencies import get_current_user
from backend.app.create_engine import get_db
from fastapi import APIRouter, Depends, HTTPException


router = APIRouter(tags=["Feedback"], dependencies=[Depends(get_db)])

@router.post("/user/gives_feedback_for_a_product", response_model=FeedbackOut, status_code=201)
async def give_feedback(
    feedback: FeedbackCreate,
    product_id: int,
    db: Session = Depends(get_db),   
    current_user: User = Depends(get_current_user),    
):
    if current_user.role != "customer":
        raise HTTPException(status_code=403, detail="You are not authorized to perform this action")
    available_product = db.query(Product).filter(Product.id == product_id).first()
    if not available_product: 
        raise HTTPException(status_code=404, detail="The product is unavailable at the moment")
    get_orders_for_current_user = db.query(Order).filter(Order.user_id == current_user.id).all()
    if not get_orders_for_current_user:
        raise HTTPException(status_code=404, detail="No orders found for this specific user")  
    order_id = get_orders_for_current_user[0].id
    
    new_feedback = Feedback(
        user_id = current_user.id,
        order_id = order_id,
        product_id = product_id,
        message = feedback.message,
        ratings = feedback.ratings
    )

    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)

    return new_feedback