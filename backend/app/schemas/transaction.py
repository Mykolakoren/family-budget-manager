from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from decimal import Decimal

from app.models.transaction import TransactionType, RecurrenceType


class TransactionBase(BaseModel):
    amount: Decimal
    description: Optional[str] = None
    notes: Optional[str] = None
    transaction_type: TransactionType
    transaction_date: datetime
    is_planned: bool = False
    is_recurring: bool = False
    recurrence_type: RecurrenceType = RecurrenceType.NONE
    recurrence_interval: int = 1
    next_occurrence: Optional[datetime] = None
    tags: Optional[str] = None
    location: Optional[str] = None
    account_id: int
    category_id: int
    budget_id: Optional[int] = None


class TransactionCreate(TransactionBase):
    original_text: Optional[str] = None


class TransactionUpdate(BaseModel):
    amount: Optional[Decimal] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    transaction_date: Optional[datetime] = None
    is_planned: Optional[bool] = None
    is_recurring: Optional[bool] = None
    recurrence_type: Optional[RecurrenceType] = None
    recurrence_interval: Optional[int] = None
    next_occurrence: Optional[datetime] = None
    tags: Optional[str] = None
    location: Optional[str] = None
    account_id: Optional[int] = None
    category_id: Optional[int] = None
    budget_id: Optional[int] = None


class Transaction(TransactionBase):
    id: int
    user_id: int
    original_text: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TransferBase(BaseModel):
    amount: Decimal
    exchange_rate: Decimal = 1.0
    fee: Decimal = 0.0
    description: Optional[str] = None
    transfer_date: datetime
    from_account_id: int
    to_account_id: int


class TransferCreate(TransferBase):
    pass


class Transfer(TransferBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TransactionParseRequest(BaseModel):
    text: str
    user_id: int


class TransactionParseResponse(BaseModel):
    amount: Optional[Decimal] = None
    description: Optional[str] = None
    transaction_type: Optional[TransactionType] = None
    category_name: Optional[str] = None
    account_name: Optional[str] = None
    currency: Optional[str] = None
    confidence: float = 0.0
    suggestions: list = []