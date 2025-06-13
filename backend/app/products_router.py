from backend.app.schema import ProductCreate, ProductOut
from backend.app.models import Product, Category, User
from backend.app.create_engine import get_db
from backend.app.dependencies import get_current_user
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from sqlalchemy import select, func

router = APIRouter(tags=["Products"], dependencies=[Depends(get_db)])


@router.post("/add_product_to_category/{category_id}")
async def add_product_to_category(
    category_id: int,
    product: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins are allowed to perform this task")
    results = await db.execute(select(Category).where(
        Category.id == category_id
    ))
    existing_category = results.scalar_one_or_none()
    if not existing_category:
        logging.error(f"Category with id {category_id} does not exist")
        raise HTTPException(status_code=404, detail="Category not found")
    
    new_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        quantity=product.quantity,
        category_id=category_id,
        image_url=product.image_url
    )

    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    logging.info(f"Product {new_product.name} added to category {category_id}") 
    return new_product

@router.get("/view_products_by_category/{category_id}", response_model=list[ProductOut])
async def view_products_by_category(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    all_products = await db.execute(select(Product).where(
        Product.category_id == category_id))
    products = all_products.scalars().all()

    if not products:
        logging.warning(f"No products found for the category with id {category_id}")
        raise HTTPException(status_code=404, detail="No product found for this category")
    
    logging.info(f"Products retrieved for category {category_id}: {len(products)} products found")
    return products

@router.get("/view_all_products", response_model=list[ProductOut])
async def view_all_products(
    db: AsyncSession = Depends(get_db)
):
    all_products = await db.execute(select(Product))
    products = all_products.scalars().all()

    if not products:
        logging.warning("No products found in the database")
        raise HTTPException(status_code=404, detail="No products available")
    
    logging.info(f"Total products retrieved: {len(products)}")
    return products

@router.get("/view_product/{product_id}", response_model=ProductOut)
async def view_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if not product:
        logging.error(f"Product with id {product_id} does not exist")
        raise HTTPException(status_code=404, detail="Product not found")
    
    logging.info(f"Product retrieved: {product.name}")
    return product

@router.delete("/delete_product/{product_id}")
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins are allowed to perform this task")
    
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if not product:
        logging.error(f"Product with id {product_id} does not exist")
        raise HTTPException(status_code=404, detail="Product not found")
    
    await db.delete(product)
    await db.commit()
    logging.info(f"Product {product.name} deleted successfully")
    return {"detail": "Product deleted successfully"}