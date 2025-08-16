from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from decimal import Decimal

from app.models.account import AccountType, CurrencyCode


class AccountBase(BaseModel):
    name: str
    description: Optional[str] = None
    account_type: AccountType
    currency: CurrencyCode
    initial_balance: Decimal = 0.00
    is_included_in_total: bool = True
    bank_name: Optional[str] = None
    card_last_four: Optional[str] = None
    color: str = "#28a745"
    icon: Optional[str] = None


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    is_included_in_total: Optional[bool] = None
    bank_name: Optional[str] = None
    card_last_four: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None


class Account(AccountBase):
    id: int
    balance: Decimal
    is_active: bool
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AccountBalance(BaseModel):
    account_id: int
    account_name: str
    currency: CurrencyCode
    balance: Decimal
    
    class Config:
        from_attributes = True