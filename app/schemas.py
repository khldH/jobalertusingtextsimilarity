from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    job_description: Optional[str] = None
    is_all: Optional[bool] = False
    follows: Optional[List] = []
    is_active: Optional[bool] = False


class OrganizationCreate(BaseModel):
    email: EmailStr
    organization: Optional[str] = None
    username: Optional[str] = False


class GenerateOrgLoginLink(BaseModel):
    email: EmailStr


class PostCreate(BaseModel):
    title: str
    organization: Optional[str] = None
    type: Optional[str] = None
    location: Optional[str] = None
    end_date: Optional[str] = None
    category: Optional[str] = None
    details: Optional[str] = None


class VerificationToken(BaseModel):
    token: str
    # is_authenticated: bool
    # is_verified: bool
