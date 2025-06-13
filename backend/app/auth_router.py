from unittest import result
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.security import OAuth2PasswordRequestForm
from backend.app.models import User
from backend.app.schema import UserCreate, UserOut, UserUpdate
from backend.app.create_engine import get_db
from backend.app.dependencies import get_current_user
from backend.app.auth_handler import (
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
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    if not user.hostel_block or not user.room_number:
        raise HTTPException(status_code=400, detail="Hostel block and room number are required")
    # if user.role not in ["customer", "admin"]:
    #     raise HTTPException(status_code=400, detail="Invalid role. Must be 'customer' or 'admin'")
    if user.hostel_block and user.room_number:
        user.is_outside_campus = False
    else:
        user.is_outside_campus = True

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
    if not any(char in "!@#$%^&*()-_+=<>?/|{}[].:;\"'`~" for char in user.password):
        raise HTTPException(status_code=400, detail="Password must contain at least one special character")
    phone_number_exists = db.execute(User).filter(User.phone_number == user.phone_number).first()
    if phone_number_exists:
        raise HTTPException(status_code=400, detail="Phone number already registered")
    if user.phone_number is None:
        raise HTTPException(status_code=400, detail="Phone number is required")
    if user.phone_number and len(user.phone_number) < 10:
        raise HTTPException(status_code=400, detail="Phone number must be at least 10 digits long")
    if not user.phone_number.startswith("254") and len(user.phone_number) == 12:
        raise HTTPException(status_code=400, detail="Phone number must start with '254' and be 12 digits long")
    
    full_name = user.full_name if user.full_name else user.email.split("@")[0]
    hashed = hash_password(user.password)
    new_user = User(
        full_name=full_name,
        email=user.email,
        hashed_password=hashed,
        role=user.role,
        hostel_block=user.hostel_block,
        phone_number=user.phone_number,
        room_number=user.room_number,
        is_outside_campus=user.is_outside_campus
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalars().first()    
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
    db: AsyncSession = Depends(get_db)
):
    updated_data = user_update.dict(exclude_unset=True)
    if "password" in updated_data:
        """ You cannot update password using this endpoint. """
        raise HTTPException(status_code=400, detail="Password cannot be updated using this endpoint.")
    
    
    if "email" in updated_data:
        result = await db.execute(select(User).where(User.email == updated_data["email"])) 
        existing_user = result.scalars().first()     
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(status_code=400, detail="Email already registered")
    
        current_user.email = updated_data["email"]    
    
    if "phone_number" in updated_data:
        phone_number = str(updated_data["phone_number"]).strip()
        if len(phone_number) < 12:
            raise HTTPException(status_code=400, detail="Phone number must be at least 12 digits long")
        if not phone_number.startswith("254"):
            raise HTTPException(status_code=400, detail="Phone number must start with '254'")
        
        result = await db.execute(select(User).where(User.phone_number == phone_number))
        existing_user = result.scalars().first()
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(status_code=400, detail="Phone number already registered")

        current_user.phone_number = phone_number
 

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
        
    await db.commit()
    await db.refresh(current_user)
    return current_user

@router.patch("/update_password")
async def update_password(
    current_password: str = Body(...),
    new_password: str = Body(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
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
    await db.commit()
    await db.refresh(current_user)
    return {"message": "Password updated successfully"}

# Delete user by ID
@router.delete("/delete_user/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You are not authorized to perform this action")
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()  
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    await db.commit()
    return {"detail": "User deleted successfully"}

