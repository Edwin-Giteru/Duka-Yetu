from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import enum

from backend.app.db.schemas import order_item
Base = declarative_base()



# Enum for Order Status
class OrderStatus(enum.Enum):
    PENDING = "Pending"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

class OrderPayment(enum.Enum):
    PENDING= "Pending"
    COMPLETED ="Completed"
    CANCELLED ="Cancelled"

class UserRole(enum.Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"


# User Model
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    hostel_block = Column(String(50), nullable=False)
    room_number = Column(String(50), nullable=False)
    role = Column(String(50), nullable=False, default=UserRole.CUSTOMER)
    is_outside_campus = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())

    orders = relationship("Order", back_populates="user")
    feedback = relationship("Feedback", back_populates="user")
    order_items = relationship("OrderItem", back_populates="user")
# Product Model

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    stock = Column(Integer, nullable=False, default=0)    
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    image_url = Column(String(100), nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())

    category = relationship("Category", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")


# Category Model
class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())

    products = relationship("Product", back_populates="category")


# Order Model
class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING)
    created_at = Column(DateTime, nullable=False, default=func.now())
    delivery_address = Column(String(100), nullable=False) 
    total_price = Column(Float, nullable=False)  
    payment_status = Column(Enum(OrderPayment), nullable=False, default=OrderPayment.PENDING) 

    user = relationship("User", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")



# OrderItem Model
class OrderItem(Base):
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=True)  # <-- Add this
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)    # <-- Add this
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_per_item = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)

    order = relationship("Order", back_populates="order_items")
    user = relationship("User", back_populates="order_items")  # <-- Add this
    product = relationship("Product", back_populates="order_items")


# Feedback Model
class Feedback(Base):
    __tablename__ = 'feedback'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())

    user = relationship("User", back_populates="feedback")