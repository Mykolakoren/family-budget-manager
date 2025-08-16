from pydantic import BaseModel
from typing import Optional
from enum import Enum

class BudgetType(str, Enum):
    FAMILY = "family"
    UNBOX = "unbox"
    NEOSCHOOL = "neoschool"
    PERSONAL = "personal"

class BudgetBase(BaseModel):
    name: str
    description: Optional[str] = None
    budget_type: BudgetType
    default_currency: str = "GEL"
    
class BudgetCreate(BudgetBase):
    pass
    
class BudgetResponse(BudgetBase):
    id: int
    owner_id: int
    is_active: bool
    
    class Config:
        orm_mode = True