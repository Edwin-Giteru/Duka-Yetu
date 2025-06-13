from backend.app.create_engine import get_db
from backend.app.models import Category, Product
from backend.app.schema import CategoryCreate, CategoryOut, CategoryGet
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.app.dependencies import get_current_active_user, get_current_user
from backend.app.models import User

router = APIRouter(tags=["Category"], dependencies=[Depends(get_db)])

def is_admin_current_user(current_user):
        return get_current_active_user(current_user)
    

@router.post("/create_category", response_model=CategoryOut)
async def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):         
   if current_user.role == "admin":
        existing_category = db.query(Category).filter(Category.name == category.name).first()
        if existing_category:
            raise HTTPException(status_code=400, detail="Category already exists")
        new_category = Category(
                name=category.name,
                description=category.description,
            )
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        return new_category      
   

@router.get("/get_all_categories")
async def get_all_categories(
        db: Session = Depends(get_db),  
        current_user: User = Depends(get_current_user)
):
    if current_user.role == "admin":
        """
        Get all categories.
        """
        categories = db.query(Category).all()  
        if not categories:
            raise HTTPException(status_code=404, detail="No categories found")      
        return categories
    else:
        raise HTTPException(status_code=403, detail="You are not authorized to perform this action")

@router.get("/get_category/{category_id}", response_model=CategoryOut)
async def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a category by ID.
    """
    if current_user.role == "admin":
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return category
    else:
        raise HTTPException(status_code=403, detail="You are not authorized to perform this action")
    
@router.put("/update_category/{category_id}", response_model=CategoryOut)
async def update_category(
    category_id: int,
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a category by ID.
    """
    if current_user.role == "admin":
        existing_category = db.query(Category).filter(Category.id == category_id).first()
        if not existing_category:
            raise HTTPException(status_code=404, detail="Category not found")
        existing_category.name = category.name
        existing_category.description = category.description
        db.commit()
        db.refresh(existing_category)
        return existing_category
    else:
        raise HTTPException(status_code=403, detail="You are not authorized to perform this action")

@router.delete("/delete_category/{category_id}")
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a category by ID.
    """
    if current_user.role == "admin":
        existing_category = db.query(Category).filter(Category.id == category_id).first()
        if not existing_category:
            raise HTTPException(status_code=404, detail="Category not found")
        db.delete(existing_category)
        db.commit()
        return {"detail": "Category deleted successfully"}
    else:
        raise HTTPException(status_code=403, detail="You are not authorized to perform this action")

@router.get("/get_products_related_to_this_category{category_id}")
async def get_products_for_this_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Getting products related to this category
    """
    if current_user.role == "admin":
        products_under_category = db.query(Product).filter(Product.category_id == category_id).all()
        if not products_under_category:
            raise HTTPException(status_code=404, detail="No product found for this category")
        return products_under_category
    else:
        raise HTTPException(status_code=403, detail="You are not authorized to perform  this task")