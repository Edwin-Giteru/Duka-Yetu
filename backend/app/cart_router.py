from backend.app.models import CartItem, User, Product
from backend.app.dependencies import get_current_user
from backend.app.schema import OrderItemCreate, OrderItemOut
from backend.app.create_engine import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select

router = APIRouter(tags=["Cart"], dependencies=[Depends(get_db)])

@router.post("/add_to_cart")
async def add_to_cart(
    product_id: int,
    orderitems: OrderItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add items to cart
    """
    if current_user.role != "customer":
        raise HTTPException(status_code=403, detail="Only customers are allowed to perform this task")
    results = await db.execute(select(Product).where(Product.id == product_id))
    available_product = results.scalars().first()
    if not available_product:
        raise HTTPException(status_code=404, detail="We don't have the product at the moment")

    message = "Item(s) added to cart successfully."
    # If requested quantity is more than stock, set to available stock and inform user
    if available_product.stock < orderitems.quantity:
        orderitems.quantity = available_product.stock
        message = f"Only {available_product.stock} items are available. Quantity set to available stock."

    # Update the product stock
    if available_product.stock == 0:
        raise HTTPException(status_code=404, detail="This product is out of stock")
    available_product.stock -= orderitems.quantity

    cart_item = CartItem(
        product_id=product_id,
        quantity=orderitems.quantity,
        user_id = current_user.id,
        price_per_item=available_product.price,
        subtotal=available_product.price * orderitems.quantity
    )
    db.add(cart_item)
    await db.commit()
    await db.refresh(cart_item)
    return {"cart_item": cart_item, "message": message}


@router.get("/view_cart{user_id}")
async def view_cart(        
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    View items in the cart
    """
    if current_user.role != "customer":
        raise HTTPException(status_code=403, detail="You are not allowed to perform this task")
    all = await db.execute(select(CartItem).where(
        CartItem.user_id == current_user.id,
        CartItem.order_id == None
        ))
    get_all_products = all.scalars().all()

    if not get_all_products:
        raise HTTPException(status_code=404, detail="Oops!.., You don't have any items in your cart at the moment")
    return get_all_products