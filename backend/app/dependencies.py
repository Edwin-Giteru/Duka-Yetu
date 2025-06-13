# auth/dependencies.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session
from backend.app.auth_handler import decode_access_token
from backend.app.models import User
from backend.app.create_engine import get_db
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    email = decode_access_token(token)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Check if current user is admin
async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.role == "admin":
        return current_user
    else:
        raise HTTPException(status_code=403, detail="You are not authorized to perform this action")