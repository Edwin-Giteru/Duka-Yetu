from backend.app.db.model.models import Order, OrderItem, User
from backend.app.db.create_engine import get_db
from sqlalchemy.orm import Session
from backend.app.Controllers.auth.dependencies import get_current_user
from fastapi import APIRouter, HTTPException, Depends
from backend.app.db.schemas import order_item
from backend.app.db.schemas.order import OrderCreate, OrderOut, OrderUpdate

router = APIRouter(tags=["Order"], dependencies=[Depends(get_db)])


@router.post("/order/place_an_order_by_the_customer" ,response_model=OrderOut)
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
    
    cart_items = db.query(OrderItem).filter(OrderItem.user_id == current_user.id).all()
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

@router.get("/order/all_orders_for_a_user{user_id}")
async def get_all_orders_for_a_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all the users order history
    """
    if current_user.role != "customer":
        raise HTTPException(status_code=403, detail="You are not authorized to perform this task")
    your_order_history = db.query(Order).filter(Order.user_id == current_user.id).all()
    if not your_order_history:
        raise HTTPException(status_code=404, detail="You don't have any orders placed currently")
    
    return your_order_history

@router.get("/order/{order_id}", response_model=OrderOut)
async def get_order_detail(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    # Only the owner or an admin can view the order
    if order.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to view this order")
    return order