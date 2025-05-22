from backend.app.db.model.models import OrderItem, User, Product
from backend.app.Controllers.auth.dependencies import get_current_user
from backend.app.db.schemas.order_item import OrderItemCreate, OrderItemOut
from backend.app.db.create_engine import get_db
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends

router = APIRouter(tags=["Cart"], dependencies=[Depends(get_db)])

@router.post("/add_to_cart")
async def add_to_cart(
    product_id: int,
    orderitems: OrderItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add items to cart
    """
    if current_user.role != "customer":
        raise HTTPException(status_code=403, detail="Only customers are allowed to perform this task")
    available_product = db.query(Product).filter(Product.id == product_id).first()
    if not available_product:
        raise HTTPException(status_code=404, detail="We don't have the product at the moment")

    message = "Item(s) added to cart successfully."
    # If requested quantity is more than stock, set to available stock and inform user
    if available_product.stock < orderitems.quantity:
        orderitems.quantity = available_product.stock
        message = f"Only {available_product.stock} items are available. Quantity set to available stock."

    # Update the product stock
    if available_product.stock  <= 0:
        raise HTTPException(status_code=404, detail="This product is out of stock")
    available_product.stock -= orderitems.quantity

    cart_item = OrderItem(
        product_id=product_id,
        quantity=orderitems.quantity,
        user_id = current_user.id,
        price_per_item=available_product.price,
        subtotal=available_product.price * orderitems.quantity
    )
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    return {"cart_item": cart_item, "message": message}


@router.get("/view_cart{user_id}")
async def view_cart(        
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    View items in the cart
    """
    if current_user.role != "customer":
        raise HTTPException(status_code=403, detail="You are not allowed to perform this task")
    get_all_products = db.query(OrderItem).filter(OrderItem.user_id == current_user.id).all()

    if not get_all_products:
        raise HTTPException(status_code=404, detail="Oops!.., No items found in the cart for this user")
    return get_all_products