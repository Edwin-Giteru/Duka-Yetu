from backend.app.db.create_engine import get_db
from backend.app.db.model.models import Product
from backend.app.db.schemas.product import ProductCreate, ProductOut
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.Controllers.auth.dependencies import  get_current_user
from backend.app.db.model.models import User
from backend.app.db.model.models import Category

router = APIRouter(tags=["Product"], dependencies=[Depends(get_db)])

@router.post("/create_product", response_model=ProductOut)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "admin":
        existing_product = db.query(Product).filter(Product.name == product.name).first()
        if existing_product:
            raise HTTPException(status_code=400, detail="This product is already registered, please check the name again or contact support")
        
        # check if category exists
        category = db.query(Category).filter(Category.id == product.category_id).first()
        if not category:
            raise HTTPException(status_code = 400, detail="Category does not exist")
        
        new_product = Product(
            name=product.name,
            description=product.description,
            price=product.price,
            quantity=product.quantity,
            category_id=product.category_id,
            image_url=product.image_url,
            stock = product.quantity
        )              
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        return new_product
    
@router.put("/update_product_details{product_id}", response_model=ProductOut)
async def update_product_details(
    product_id: int,
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "admin":
        product_exists = db.query(Product).filter(Product.id == product_id).first()
        if not product_exists:
            raise HTTPException(status_code=404, detail="Product requested is not available at the moment")
        
        product_exists.name = product.name
        product_exists.description  = product.description
        product_exists.price = product.price
        product_exists.quantity = product.quantity
        product_exists.category_id = product.category_id
        product_exists.image_url = product.image_url
        product_exists.stock = product_exists.stock + product.quantity
    
        db.commit()
        db.refresh(product_exists)
        return product_exists
    else:
        raise HTTPException(status_code=403, detail="You are not authorized to perform this task")
