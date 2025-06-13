from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import enum
from typing import List
from sqlalchemy.orm import Mapped

Base = declarative_base()



# Enum for Order Status
class OrderStatus(enum.Enum):
    PENDING = "Pending"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

class OrderPayment(enum.Enum):
    PENDING= "Pending"
    COMPLETED ="Completed"   

class UserRole(enum.Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"

class paymentStatus(enum.Enum):
    INITIATED = "initiated"
    COMPLETED = "completed"
    FAILED = "failed"


# User Model
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), index=True)
    email = Column(String(255), unique=True, index=True)
    phone_number = Column(String(20), nullable=True, unique=True)
    hashed_password = Column(String(255), nullable=False)
    hostel_block = Column(String(50), nullable=False)
    room_number = Column(String(50), nullable=False)
    role = Column(String(50), nullable=False, default=UserRole.CUSTOMER.value)
    is_outside_campus = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())

    orders = relationship("Order", back_populates="user")
    feedback = relationship("Feedback", back_populates="user")
    order_items = relationship("CartItem", back_populates="user")
    payments = relationship("Payment", back_populates="user")

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
    order_items = relationship("CartItem", back_populates="product")


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
    user_id = Column(Integer,ForeignKey("users.id"), index=True)
    delivery_address = Column(String(100), nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(String(100), default=OrderPayment.PENDING.value)
    mpesa_checkout_request_id = Column(String(100), nullable=True)
    mpesa_transaction_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())
    payment_status = Column(Enum(OrderPayment), nullable=False, default=OrderPayment.PENDING.value) 

    user = relationship("User", back_populates="orders")
    order_items: Mapped[List["CartItem"]] = relationship("CartItem", back_populates="order", cascade="all, delete-orphan")
    payment = relationship("Payment", back_populates="order", uselist=False, cascade="all, delete-orphan")



# CartItem Model
class CartItem(Base):
    __tablename__ = 'cart_items'

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id', ondelete="CASCADE"), nullable=True)  
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=True) 
    product_id = Column(Integer, ForeignKey('products.id', ondelete="SET NULL"), nullable=True)   
    quantity = Column(Integer, nullable=False)
    price_per_item = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)

    order = relationship("Order", back_populates="order_items")
    user = relationship("User", back_populates="order_items")  
    product = relationship("Product", back_populates="order_items")

# Feedback Model
class Feedback(Base):
    __tablename__ = 'feedback'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable = True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable = True)
    message = Column(Text, nullable=False)
    ratings =  Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())

    user = relationship("User", back_populates="feedback")

# Payment Model
class Payment(Base):
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    order_id = Column(Integer, ForeignKey('orders.id'), index=True, nullable=False) 
    checkout_request_id = Column(String(100), unique=True)
    merchant_request_id = Column(String(100), nullable=True)
    amount = Column(Float, nullable=False)
    phone_number = Column(String(50), nullable=False)
    transaction_id = Column(String(100), nullable=True)
    result_code = Column(Integer, nullable=True)
    result_desc = Column(Text, nullable=True)
    status = Column(String(100), default=paymentStatus.INITIATED.value)
    created_at = Column(DateTime, default=func.now())

    order = relationship("Order", back_populates="payment")
    user = relationship("User", back_populates="payments")