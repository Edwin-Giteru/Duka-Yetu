from hmac import new
from backend.app.db.model.models import Order, OrderItem, User
from backend.app.db.create_engine import get_db
from sqlalchemy.orm import Session
from backend.app.Controllers.auth.dependencies import get_current_user
from fastapi import APIRouter, HTTPException, Depends
from backend.app.db.schemas import order_item
from backend.app.db.schemas.order import OrderCreate, OrderOut, OrderUpdate

router = APIRouter(tags=["Order"], dependencies=[Depends(get_db)])


@router.post("/place_an_order_by_the_customer" ,response_model=OrderOut)
async def create_an_order(   
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "customer":
        raise HTTPException(status_code=403, detail="Only customers can place order")
    if current_user.is_outside_campus:
        delivery_address = "Outside Campus"
    else:
        delivery_address = f"{current_user.hostel_block}, Room {current_user.room_number}"
    
    cart_items = db.query(OrderItem).filter(User.id == current_user.id).all()
    if not cart_items:
        raise HTTPException(status_code=400,detail="No items in cart to place an order")
    
    total_price = sum(item.subtotal for item in cart_items)

    new_order = Order(
        user_id = current_user.id,
        payment_status = order.payment_status,
        order_items=cart_items,
        delivery_address=delivery_address,
        total_price=total_price
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    for item in cart_items:
        item.order_id = new_order.id
    db.commit()
    
    return new_order