from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class CategoryType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"


class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(SQLEnum(CategoryType), nullable=False)
    color = Column(String(7), default="#007bff")  # Hex color code
    icon = Column(String(50), nullable=True)  # Icon name/code
    is_default = Column(Boolean, default=False)  # System predefined categories
    is_active = Column(Boolean, default=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # NULL for default categories
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="categories")
    parent = relationship("Category", remote_side=[id])
    children = relationship("Category")
    transactions = relationship("Transaction", back_populates="category")
    budget_limits = relationship("BudgetLimit", back_populates="category")