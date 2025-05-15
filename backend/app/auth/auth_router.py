from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from backend.app.db.model.models import User
from backend.app.db.schemas.user import UserCreate, UserOut, UserUpdate
from backend.app.db.create_engine import get_db
from backend.app.auth.dependencies import get_current_user
from backend.app.auth.auth_handler import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    )
from datetime import timedelta

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

router = APIRouter(tags=["Auth"], dependencies=[Depends(get_db)])


@router.post("/register", response_model=UserOut)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user =  db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    if not user.hostel_block or not user.room_number:
        raise HTTPException(status_code=400, detail="Hostel block and room number are required")
    if user.role not in ["customer", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid role. Must be 'customer' or 'admin'")
    if user.is_outside_campus is None:
        raise HTTPException(status_code=400, detail="is_outside_campus must be a boolean value")
    if user.password is None:
        raise HTTPException(status_code=400, detail="Password is required")
    if len(user.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
    if not any(char.isdigit() for char in user.password):
        raise HTTPException(status_code=400, detail="Password must contain at least one digit")
    if not any(char.isalpha() for char in user.password):
        raise HTTPException(status_code=400, detail="Password must contain at least one letter")
    if not any(char in "!@#$%^&*()-_+=<>?/|{}[]:;\"'`~" for char in user.password):
        raise HTTPException(status_code=400, detail="Password must contain at least one special character")
    
    hashed = hash_password(user.password)
    new_user = User(
        full_name=user.full_name,
        email=user.email,
        hashed_password=hashed,
        role=user.role,
        hostel_block=user.hostel_block,
        room_number=user.room_number,
        is_outside_campus=user.is_outside_campus
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid password")
    
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token(
        data={"sub": user.email}, expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh")
def refresh_token(refresh_token: str):
    email = verify_refresh_token(refresh_token)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    
    new_access_token = create_access_token(
        data={"sub": email}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": new_access_token, "token_type": "bearer"}


@router.put("/update_user_details_without_password")
async def update_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    updated_data = user_update.dict(exclude_unset=True)
    if "password" in updated_data:
        """ You cannot update password using this endpoint. """
        raise HTTPException(status_code=400, detail="Password cannot be updated using this endpoint.")
    
    if "email" in updated_data:
        existing_user =  db.query(User).filter(User.email == updated_data["email"]).first()
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(status_code=400, detail="Email already registered")
    
        current_user.email = updated_data["email"]        

    if "hostel_block" in updated_data  or "room_number" in updated_data:
        new_block = updated_data.get("hostel_block", current_user.hostel_block)
        new_room = updated_data.get("room_number", current_user.room_number)

        if new_block and not new_room:
            raise HTTPException(status_code=400, detail="Room number is required if new hostel block is provided")  
        if new_room and not new_block:
            raise HTTPException(status_code=400, detail="Hostel block is required when updating room number")
        
        if new_block and new_block not in ["CBD", "Maringo", "Tatton", "Ruwenzori", "Taifa", "Mama Ngina", "Uganda", "Hollywood"]:
            raise HTTPException(status_code=400, detail="Invalid hostel block")
        
        current_user.hostel_block = new_block
        current_user.room_number = new_room
        
    if "is_outside_campus" in updated_data:
        """ You are already registered as living in the hostel. """
        raise HTTPException(status_code=400, detail="You are already registered as living in the hostel.")
        
    db.commit()
    db.refresh(current_user)
    return current_user

@router.patch("/update_password")
async def update_password(
    current_password: str = Body(...),
    new_password: str = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(current_password, current_user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect current password")
    
    if len(new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
    if not any(char.isdigit() for char in new_password):
        raise HTTPException(status_code=400, detail="Password must contain at least one digit")
    if not any(char.isalpha() for char in new_password):
        raise HTTPException(status_code=400, detail="Password must contain at least one letter")
    if not any(char in "!@#$%^&*()-_+=<>?/|{}[]:;\"'`~" for char in new_password):
        raise HTTPException(status_code=400, detail="Password must contain at least one special character")
    
    hashed = hash_password(new_password)
    current_user.hashed_password = hashed
    db.commit()
    db.refresh(current_user)
    return {"message": "Password updated successfully"}

# Delete user by ID
@router.delete("/delete_user/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You are not authorized to perform this action")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"detail": "User deleted successfully"}