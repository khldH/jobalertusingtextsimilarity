from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    job_description: Optional[str] = None
    is_all: Optional[bool] = False
    follows: Optional[List] = []
    is_active: Optional[bool] = False


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
