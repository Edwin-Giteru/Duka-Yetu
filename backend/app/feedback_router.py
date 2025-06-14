from backend.app.models import Feedback, User, Product, Order
from backend.app.schema import FeedbackCreate, FeedbackOut
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.dependencies import get_current_user
from backend.app.create_engine import get_db
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload


router = APIRouter(tags=["Feedback"], dependencies=[Depends(get_db)])

@router.post("/user/gives_feedback_for_a_product", response_model=FeedbackOut, status_code=201)
async def give_feedback(
    feedback: FeedbackCreate,
    product_id: int,
    db: AsyncSession = Depends(get_db),   
    current_user: User = Depends(get_current_user),    
):
    if current_user.role != "customer":
        raise HTTPException(status_code=403, detail="You are not authorized to perform this action")
    products = await db.execute(select(Product).where(Product.id == product_id))
    available_product = products.scalars().first()
    if not available_product: 
        raise HTTPException(status_code=404, detail="The product is unavailable at the moment")
    orders_for_current_user = await db.execute(select(Order).where(Order.user_id == current_user.id))
    get_orders_for_current_user = orders_for_current_user.scalars().all()
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
    await db.commit()
    await db.refresh(new_feedback)

    return new_feedback