from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, validator

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


class IssuedBookBase(BaseModel):
    student_name: str
    book_title: str
    issue_date: Optional[datetime]
    due_date: Optional[datetime]
    return_date: Optional[datetime]
    is_returned: bool


class IssuedBookCreate(BaseModel):
    student_name: str
    book_title: str

    @validator("student_name", "book_title")
    def not_empty(cls, v):
        if not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()


class IssuedBookResponse(BaseModel):
    id: UUID
    student_name: str
    book_title: str
    issue_date: datetime
    due_date: datetime
    return_date: Optional[datetime]
    is_returned: bool

    class Config:
        orm_mode = True


class ReturnBookRequest(BaseModel):
    book_title: str

    @validator("book_title")
    def not_empty(cls, v):
        if not v.strip():
            raise ValueError("Book title cannot be empty")
        return v.strip()


class ReturnIssuedBookResponse(BaseModel):
    issued_book_id: UUID
    student_name: str
    book_title: str
    return_date: datetime
    is_returned: bool
    message: Optional[str] = None
    fine_amount: Optional[Decimal] = None

    class Config:
        from_attributes = True
