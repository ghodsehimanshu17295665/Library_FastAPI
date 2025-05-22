from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models import GenderEnum, UserRoleEnum


# Base schema (shared fields)
class AuthorBase(BaseModel):
    name: str
    email: EmailStr
    nationality: Optional[str] = None


# Schema for creating an author
class AuthorCreate(AuthorBase):
    pass


# Schema for returning author data
class AuthorResponse(AuthorBase):
    id: UUID
    created_at: datetime

    class Config:
        orm_mode = True  # Important to work with SQLAlchemy models


class CategoryBase(BaseModel):
    name: str
    description: str


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: UUID

    class Config:
        orm_mode = True


# Shared fields
class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: Optional[UserRoleEnum] = UserRoleEnum.STUDENT
    enroll_number: Optional[str] = None
    mobile_number: Optional[str] = None
    gender: Optional[GenderEnum] = None
    course_id: Optional[UUID] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# For creating new user (includes password)
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=64)


# For response (excludes password)
class UserResponse(UserBase):
    id: UUID
    created_at: datetime

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    name: Optional[str]
    password: Optional[str]
    enroll_number: Optional[str] = None
    mobile_number: Optional[str]
    gender: Optional[GenderEnum] = None

    class Config:
        orm_mode = True
