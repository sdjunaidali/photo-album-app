from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    groups: List[str]  # List of group names user is part of

    class Config:
        orm_mode = True

# Schema for Token (JWT Response)
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: Optional[datetime] = None