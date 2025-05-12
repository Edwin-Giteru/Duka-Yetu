from sqlalchemy import Column, Integer, String, DateTime, Boolean
from backend.app.db.models.base import Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    full_name  = Column(String(100), index=True, required=True)
    email = Column(String(255), unique=True, index=True, required=True)
    hashed_password = Column(String(255), encrypted=True, required=True)
    hostel_block = Column(String(50), nullable=False)
    room_number = Column(String(50), nullable=False)
    is_outside_campus = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())

    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    feedback = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")
