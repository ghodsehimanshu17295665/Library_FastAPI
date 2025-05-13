import enum
import uuid
from datetime import datetime
from typing import List

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
    nationality: Mapped[str] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    books: Mapped[List["Book"]] = relationship(back_populates="author")

    def __repr__(self):
        return f"<Author(id={self.id}, name='{self.name}', email='{self.email}')>"


class Category(Base):
    __tablename__ = "categories"  # plural for consistency

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(35), nullable=False)
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
    publication_date: Mapped[datetime] = mapped_column(DateTime)
    quantity: Mapped[int] = mapped_column(Integer)

    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("authors.id")
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("categories.id")
    )

    author: Mapped["Author"] = relationship(back_populates="books")
    category: Mapped["Category"] = relationship(back_populates="books")

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

    def __repr__(self):
        return f"<Course(id={self.id}, name='{self.name}', year='{self.year.name}')>"


class Student(Base):
    __tablename__ = "students"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    enroll_number: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    mobile_number: Mapped[str] = mapped_column(String(15), nullable=False)
    gender: Mapped[str] = mapped_column(
        Enum("Male", "Female", "Other", name="gender_enum"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("courses.id")
    )
    course: Mapped["Course"] = relationship()

    issued_books: Mapped[List["IssuedBook"]] = relationship(back_populates="student")

    def __repr__(self):
        return f"<Student(id={self.id}, name='{self.name}', enroll_number='{self.enroll_number}')>"


class IssuedBook(Base):
    __tablename__ = "issued_books"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    issue_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    due_date: Mapped[datetime] = mapped_column(DateTime)
    return_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    is_returned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("students.id")
    )
    book_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("books.id")
    )

    student: Mapped["Student"] = relationship(back_populates="issued_books")
    book: Mapped["Book"] = relationship()

    fine: Mapped["Fine"] = relationship(back_populates="issued_book", uselist=False)

    def __repr__(self):
        return f"<IssuedBook(id={self.id}, book_id={self.book_id}, student_id={self.student_id}, returned={self.is_returned})>"


class Fine(Base):
    __tablename__ = "fines"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    issued_book_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("issued_books.id"), unique=True, nullable=True
    )
    issued_book: Mapped["IssuedBook"] = relationship(back_populates="fine")

    def __repr__(self):
        return f"<Fine(id={self.id}, amount={self.amount}, issued_book_id={self.issued_book_id})>"
