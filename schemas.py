from pydantic import BaseModel
from typing import Optional

# --- User Models (keep these as-is) ---
class UserCreate(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

# --- NEW Post Models (replace the old ones completely) ---
class PostCreate(BaseModel):
    set_number: str
    buy_price: float
    sell_price: Optional[float] = None

class PostInDB(PostCreate):
    id: int
    user_id: int
    username: str

    class Config:
        from_attributes = True

# Optional: A clean response model for public posts (same as PostInDB)
PostOut = PostInDB