from collections.abc import Set
from backend.app.models import Order, CartItem, User
from backend.app.create_engine import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.dependencies import get_current_user
from fastapi import APIRouter, HTTPException, Depends
from backend.app.schema import OrderCreate, OrderOut, OrderUpdate
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

router = APIRouter(tags=["Order"], dependencies=[Depends(get_db)])


@router.post("/order/place_an_order_by_the_customer", response_model=OrderOut)
async def create_an_order(
    order: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "customer":
        raise HTTPException(status_code=403, detail="Only customers can place order")
    if current_user.is_outside_campus:
        delivery_address = "Outside Campus"
    else:
        delivery_address = f"{current_user.hostel_block}, Room {current_user.room_number}"

    items = await db.execute(
        select(CartItem).where(
            CartItem.user_id == current_user.id,
            CartItem.order_id == None
        )
    )
    cart_items = items.scalars().all()
    cart_item_ids = set(item.product_id for item in cart_items)

    orders = await db.execute(
        select(Order)
        .options(selectinload(Order.order_items))
        .where(Order.user_id == current_user.id)
    )
    previous_orders = orders.scalars().all()
    for prev_order in previous_orders:
        order_items_ids = set(item.product_id for item in prev_order.order_items)
        if order_items_ids == cart_item_ids:
            raise HTTPException(status_code=400, detail="You have already placed an order with these items")
    if not cart_items:
        raise HTTPException(status_code=400, detail="No items in cart to place an order")

    total_price = sum(item.subtotal for item in cart_items)

    new_order = Order(
        user_id=current_user.id,
        payment_status=order.payment_status,
        order_items=cart_items,
        delivery_address=delivery_address,
        total_price=total_price
    )
    db.add(new_order)
    await db.commit()
    await db.refresh(new_order)

    for item in cart_items:
        item.order_id = new_order.id
    await db.commit() 
    await db.refresh(new_order, attribute_names=["order_items"])

    return new_order

@router.get("/order/all_orders_for_a_user{user_id}", response_model=list[OrderOut])
async def get_all_orders_for_a_user(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all the users order history
    """
    if current_user.role != "customer":
        raise HTTPException(status_code=403, detail="You are not authorized to perform this task")
    order_history = await db.execute(
        select(Order)
        .options(selectinload(Order.order_items))
        .where(Order.user_id == current_user.id)
    )
    your_order_history = order_history.scalars().all()
    if not your_order_history:
        raise HTTPException(status_code=404, detail="You don't have any orders placed currently")

    return your_order_history

@router.get("/order/{order_id}", response_model=OrderOut)
async def get_order_detail(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.order_items))
        .where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    # Only the owner or an admin can view the order
    if order.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to view this order")
    return order