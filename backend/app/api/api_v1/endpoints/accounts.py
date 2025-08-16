from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.schemas.account import Account, AccountCreate, AccountUpdate
from app.services.account_service import AccountService

router = APIRouter()


@router.get("/", response_model=List[Account])
async def read_accounts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get user's accounts."""
    account_service = AccountService(db)
    accounts = account_service.get_user_accounts(current_user.id, skip=skip, limit=limit)
    return accounts


@router.post("/", response_model=Account)
async def create_account(
    account_data: AccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Create new account."""
    account_service = AccountService(db)
    account = account_service.create(current_user.id, account_data)
    return account


@router.get("/{account_id}", response_model=Account)
async def read_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get account by ID."""
    account_service = AccountService(db)
    account = account_service.get_by_id(account_id)
    
    if not account or account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    return account


@router.patch("/{account_id}", response_model=Account)
async def update_account(
    account_id: int,
    account_data: AccountUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Update account."""
    account_service = AccountService(db)
    
    # Check if account belongs to user
    account = account_service.get_by_id(account_id)
    if not account or account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    account = account_service.update(account_id, account_data)
    return account


@router.delete("/{account_id}")
async def delete_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Delete account."""
    account_service = AccountService(db)
    
    # Check if account belongs to user
    account = account_service.get_by_id(account_id)
    if not account or account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    success = account_service.delete(account_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not delete account"
        )
    
    return {"message": "Account deleted successfully"}