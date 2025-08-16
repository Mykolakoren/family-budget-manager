from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class BudgetType(str, enum.Enum):
    FAMILY = "family"
    UNBOX = "unbox"
    NEOSCHOOL = "neoschool"
    PERSONAL = "personal"
    PROJECT = "project"


class Budget(Base):
    __tablename__ = "budgets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    budget_type = Column(SQLEnum(BudgetType), nullable=False)
    currency = Column(String(3), nullable=False)  # Primary currency for this budget
    is_active = Column(Boolean, default=True)
    is_shared = Column(Boolean, default=False)  # Can be shared with family members
    color = Column(String(7), default="#6c757d")
    
    # Budget period
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="budgets")
    transactions = relationship("Transaction", back_populates="budget")
    limits = relationship("BudgetLimit", back_populates="budget")


class BudgetLimit(Base):
    __tablename__ = "budget_limits"
    
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Numeric(15, 2), nullable=False)
    period = Column(String(20), nullable=False)  # monthly, weekly, daily
    alert_threshold = Column(Numeric(5, 2), default=80.0)  # Alert when 80% of limit is reached
    is_active = Column(Boolean, default=True)
    
    budget_id = Column(Integer, ForeignKey("budgets.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    budget = relationship("Budget", back_populates="limits")
    category = relationship("Category", back_populates="budget_limits")


class Goal(Base):
    __tablename__ = "goals"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    target_amount = Column(Numeric(15, 2), nullable=False)
    current_amount = Column(Numeric(15, 2), default=0.0)
    currency = Column(String(3), nullable=False)
    target_date = Column(DateTime(timezone=True), nullable=True)
    is_achieved = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="goals")