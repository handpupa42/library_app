from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class LoginRequest(BaseModel):
    username: str
    password: str

class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, pattern="^[a-zA-Z0-9_]+$")
    email: EmailStr
    role: Optional[str] = "librarian"

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

