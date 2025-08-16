from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class AccountType(str, enum.Enum):
    CASH = "cash"
    BANK_CARD = "bank_card"
    SAVINGS = "savings"
    INVESTMENT = "investment"
    CRYPTO = "crypto"
    PAYPAL = "paypal"
    OTHER = "other"


class CurrencyCode(str, enum.Enum):
    USD = "USD"
    EUR = "EUR"
    GEL = "GEL"
    UAH = "UAH"
    USDT = "USDT"


class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    account_type = Column(SQLEnum(AccountType), nullable=False)
    currency = Column(SQLEnum(CurrencyCode), nullable=False)
    balance = Column(Numeric(15, 2), default=0.00)
    initial_balance = Column(Numeric(15, 2), default=0.00)
    is_active = Column(Boolean, default=True)
    is_included_in_total = Column(Boolean, default=True)  # Include in total balance calculations
    bank_name = Column(String(100), nullable=True)
    card_last_four = Column(String(4), nullable=True)
    color = Column(String(7), default="#28a745")  # Hex color code
    icon = Column(String(50), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")
    transfers_from = relationship("Transfer", foreign_keys="Transfer.from_account_id", back_populates="from_account")
    transfers_to = relationship("Transfer", foreign_keys="Transfer.to_account_id", back_populates="to_account")