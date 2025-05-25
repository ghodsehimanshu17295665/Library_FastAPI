from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models import GenderEnum, UserRoleEnum, YearEnum


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


class BookBase(BaseModel):
    title: str
    publication_date: Optional[datetime] = None
    quantity: int = 0
    author_name: str
    category_name: str


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str]
    publication_date: Optional[datetime]
    quantity: Optional[int]
    author_name: Optional[str]
    category_name: Optional[str]


class BookResponse(BookBase):
    id: UUID

    model_config = {"from_attributes": True}


class CourseBase(BaseModel):
    name: str
    description: str
    year: YearEnum


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    name: str
    description: str
    year: YearEnum


class CourseResponse(CourseBase):
    id: UUID

    model_config = {"from_attributes": True}
