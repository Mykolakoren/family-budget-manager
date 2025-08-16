from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime
from enum import Enum

class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"

class Currency(str, Enum):
    GEL = "GEL"
    USD = "USD"
    EUR = "EUR"
    UAH = "UAH"
    USDT = "USDT"

class TransactionBase(BaseModel):
    amount: Decimal
    currency: Currency
    transaction_type: TransactionType
    description: Optional[str] = None
    category: Optional[str] = None
    budget_id: int
    
class TransactionCreate(TransactionBase):
    pass
    
class TransactionResponse(TransactionBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True