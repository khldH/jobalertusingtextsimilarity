from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    # name: str
    email: EmailStr
    job_description: str


class UserOut(BaseModel):
    id: int
    # name: str
    email: EmailStr
    is_active: bool
    job_description: str
    created_at: datetime

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


class JobCreate(BaseModel):
    title: str
    url: str
    created_date: str
    category: str
    organization: str
    country: str
    city: str
    source: str

    class Config:
        orm_mode = True
