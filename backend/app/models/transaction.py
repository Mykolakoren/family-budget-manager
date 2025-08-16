from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class TransactionType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class RecurrenceType(str, enum.Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Numeric(15, 2), nullable=False)
    description = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    transaction_date = Column(DateTime(timezone=True), nullable=False)
    is_planned = Column(Boolean, default=False)  # For future/planned transactions
    is_recurring = Column(Boolean, default=False)
    recurrence_type = Column(SQLEnum(RecurrenceType), default=RecurrenceType.NONE)
    recurrence_interval = Column(Integer, default=1)  # Every N days/weeks/months/years
    next_occurrence = Column(DateTime(timezone=True), nullable=True)
    original_text = Column(Text, nullable=True)  # Original input text (from bot)
    tags = Column(String(500), nullable=True)  # Comma-separated tags
    location = Column(String(255), nullable=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    budget_id = Column(Integer, ForeignKey("budgets.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    account = relationship("Account", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
    budget = relationship("Budget", back_populates="transactions")


class Transfer(Base):
    __tablename__ = "transfers"
    
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Numeric(15, 2), nullable=False)
    exchange_rate = Column(Numeric(10, 6), default=1.0)  # For currency conversion
    fee = Column(Numeric(10, 2), default=0.0)
    description = Column(String(255), nullable=True)
    transfer_date = Column(DateTime(timezone=True), nullable=False)
    
    # Foreign keys
    from_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    to_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    from_account = relationship("Account", foreign_keys=[from_account_id])
    to_account = relationship("Account", foreign_keys=[to_account_id])
    user = relationship("User")