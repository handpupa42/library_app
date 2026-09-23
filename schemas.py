from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class BookBase(BaseModel):
    title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1)
    isbn: Optional[str] = None
    year: Optional[int] = None
    genre: Optional[str] = None
    available_copies: int = Field(default=1, ge=0)


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    author: Optional[str] = Field(None, min_length=1)
    isbn: Optional[str] = None
    year: Optional[int] = None
    genre: Optional[str] = None
    available_copies: Optional[int] = Field(None, ge=0)


class BookResponse(BookBase):
    id: int

    class Config:
        from_attributes = True


class ReaderBase(BaseModel):
    full_name: str = Field(..., min_length=1)
    email: EmailStr
    phone: Optional[str] = None
    registration_date: Optional[date] = None


class ReaderCreate(ReaderBase):
    pass


class ReaderUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class ReaderResponse(ReaderBase):
    id: int

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        pattern=r"^[a-zA-Z0-9_]+$"
    )
    email: EmailStr
    role: str = "librarian"


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6)


class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

