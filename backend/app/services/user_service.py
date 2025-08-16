from typing import Optional, List
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_by_telegram_id(self, telegram_id: str) -> Optional[User]:
        """Get user by Telegram ID."""
        return self.db.query(User).filter(User.telegram_id == telegram_id).first()
    
    def get_multi(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get multiple users."""
        return self.db.query(User).offset(skip).limit(limit).all()
    
    def create(self, user_data: UserCreate) -> User:
        """Create new user."""
        db_user = User(
            email=user_data.email,
            telegram_id=user_data.telegram_id,
            telegram_username=user_data.telegram_username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            preferred_language=user_data.preferred_language,
            preferred_currency=user_data.preferred_currency,
        )
        
        if user_data.password:
            db_user.hashed_password = get_password_hash(user_data.password)
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def update(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user."""
        db_user = self.get_by_id(user_id)
        if not db_user:
            return None
        
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def delete(self, user_id: int) -> bool:
        """Delete user."""
        db_user = self.get_by_id(user_id)
        if not db_user:
            return False
        
        self.db.delete(db_user)
        self.db.commit()
        return True
    
    def authenticate(self, email: str, password: str) -> Optional[User]:
        """Authenticate user."""
        user = self.get_by_email(email)
        if not user or not user.hashed_password:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user