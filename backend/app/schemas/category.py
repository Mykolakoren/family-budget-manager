from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

from app.models.category import CategoryType


class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    type: CategoryType
    color: str = "#007bff"
    icon: Optional[str] = None
    parent_id: Optional[int] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    is_active: Optional[bool] = None
    parent_id: Optional[int] = None


class Category(CategoryBase):
    id: int
    is_default: bool
    is_active: bool
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    children: List["Category"] = []
    
    class Config:
        from_attributes = True


# Update forward references
Category.model_rebuild()