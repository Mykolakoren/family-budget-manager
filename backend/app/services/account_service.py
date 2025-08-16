from typing import Optional, List
from sqlalchemy.orm import Session
from decimal import Decimal

from app.models.account import Account
from app.schemas.account import AccountCreate, AccountUpdate


class AccountService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, account_id: int) -> Optional[Account]:
        """Get account by ID."""
        return self.db.query(Account).filter(Account.id == account_id).first()
    
    def get_user_accounts(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Account]:
        """Get user's accounts."""
        return (
            self.db.query(Account)
            .filter(Account.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def create(self, user_id: int, account_data: AccountCreate) -> Account:
        """Create new account."""
        db_account = Account(
            **account_data.dict(),
            user_id=user_id,
            balance=account_data.initial_balance
        )
        
        self.db.add(db_account)
        self.db.commit()
        self.db.refresh(db_account)
        return db_account
    
    def update(self, account_id: int, account_data: AccountUpdate) -> Optional[Account]:
        """Update account."""
        db_account = self.get_by_id(account_id)
        if not db_account:
            return None
        
        update_data = account_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_account, field, value)
        
        self.db.commit()
        self.db.refresh(db_account)
        return db_account
    
    def delete(self, account_id: int) -> bool:
        """Delete account."""
        db_account = self.get_by_id(account_id)
        if not db_account:
            return False
        
        self.db.delete(db_account)
        self.db.commit()
        return True
    
    def update_balance(self, account_id: int, amount: Decimal) -> Optional[Account]:
        """Update account balance."""
        db_account = self.get_by_id(account_id)
        if not db_account:
            return None
        
        db_account.balance += amount
        self.db.commit()
        self.db.refresh(db_account)
        return db_account