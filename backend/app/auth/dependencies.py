# auth/dependencies.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session
from backend.app.auth.auth_handler import decode_access_token
from backend.app.db.model.models import User
from backend.app.db.create_engine import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    email = decode_access_token(token)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Check if current user is admin
def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.role == "admin":
        return current_user
    else:
        raise HTTPException(status_code=403, detail="You are not authorized to perform this action")