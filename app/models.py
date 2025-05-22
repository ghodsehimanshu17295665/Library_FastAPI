import enum
import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(35), nullable=False)
    email: Mapped[str] = mapped_column(String(35), unique=True, nullable=False)
    nationality: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )  # Optional
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    books: Mapped[List["Book"]] = relationship(back_populates="author")

    def __repr__(self):
        return f"<Author(id={self.id}, name='{self.name}', email='{self.email}')>"


class Category(Base):
    __tablename__ = "categories"  # plural for consistency

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(35), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    books: Mapped[List["Book"]] = relationship(back_populates="category")

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"


class Book(Base):
    __tablename__ = "books"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    publication_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("authors.id"), nullable=False
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False
    )

    author: Mapped["Author"] = relationship(back_populates="books")
    category: Mapped["Category"] = relationship(back_populates="books")
    issued_books: Mapped[List["IssuedBook"]] = relationship(back_populates="book")

    def __repr__(self):
        return f"<Book(id={self.id}, title='{self.title}', quantity={self.quantity})>"


class YearEnum(enum.Enum):
    FIRST = 1
    SECOND = 2
    THIRD = 3
    FOURTH = 4


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    year: Mapped[YearEnum] = mapped_column(Enum(YearEnum), nullable=False)
    students: Mapped[List["User"]] = relationship(back_populates="course")

    def __repr__(self):
        return f"<Course(id={self.id}, name='{self.name}', year='{self.year.name}')>"


class GenderEnum(str, enum.Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"


class UserRoleEnum(str, enum.Enum):
    ADMIN = "admin"
    STUDENT = "student"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRoleEnum] = mapped_column(
        Enum(UserRoleEnum), default=UserRoleEnum.STUDENT, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Student-specific fields
    enroll_number: Mapped[Optional[str]] = mapped_column(
        String(30), unique=True, nullable=True
    )
    mobile_number: Mapped[Optional[str]] = mapped_column(String(15), nullable=True)
    gender: Mapped[Optional[GenderEnum]] = mapped_column(
        Enum(GenderEnum), nullable=True
    )
    course_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("courses.id"), nullable=True
    )

    course: Mapped[Optional["Course"]] = relationship(back_populates="students")
    issued_books: Mapped[List["IssuedBook"]] = relationship(back_populates="student")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"


class IssuedBook(Base):
    __tablename__ = "issued_books"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    issue_date: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    due_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    return_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_returned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    book_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("books.id"), nullable=False
    )

    student: Mapped["User"] = relationship(back_populates="issued_books")
    book: Mapped["Book"] = relationship(back_populates="issued_books")

    fine: Mapped[Optional["Fine"]] = relationship(
        back_populates="issued_book", uselist=False
    )

    def __repr__(self):
        return f"<IssuedBook(id={self.id}, book_id={self.book_id}, student_id={self.student_id}, returned={self.is_returned})>"


class Fine(Base):
    __tablename__ = "fines"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )  # Decimal for money
    date: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    issued_book_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("issued_books.id"), unique=True, nullable=False
    )
    issued_book: Mapped["IssuedBook"] = relationship(back_populates="fine")

    def __repr__(self):
        return f"<Fine(id={self.id}, amount={self.amount}, issued_book_id={self.issued_book_id})>"
