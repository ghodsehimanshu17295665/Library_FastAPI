from datetime import datetime, timedelta
from decimal import Decimal
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_user
from app.database import get_db

router = APIRouter(prefix="/issued-books", tags=["Issued Books"])


@router.get("/", response_model=List[schemas.IssuedBookResponse])
def get_all_issued_books(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can view issued books")

    issued_books = db.query(models.IssuedBook).all()
    result = []
    for issued in issued_books:
        result.append(
            schemas.IssuedBookResponse(
                id=issued.id,
                student_name=issued.student.name,
                book_title=issued.book.title,
                issue_date=issued.issue_date,
                due_date=issued.due_date,
                return_date=issued.return_date,
                is_returned=issued.is_returned,
            )
        )
    return result


@router.post(
    "/", response_model=schemas.IssuedBookResponse, status_code=status.HTTP_201_CREATED
)
def issue_book(
    issue_book: schemas.IssuedBookCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can issue books.")

    if issue_book.student_name != current_user.name:
        raise HTTPException(
            status_code=403, detail="Students can only issue books for themselves."
        )

    student = (
        db.query(models.User)
        .filter(models.User.name == issue_book.student_name)
        .first()
    )
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    book = (
        db.query(models.Book).filter(models.Book.title == issue_book.book_title).first()
    )
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    already_issued = (
        db.query(models.IssuedBook)
        .filter(
            models.IssuedBook.book_id == book.id,
            models.IssuedBook.student_id == student.id,
            models.IssuedBook.is_returned == False,
        )
        .first()
    )

    if already_issued:
        raise HTTPException(
            status_code=400, detail="Book is already issued and not returned"
        )

    if book.quantity <= 0:
        raise HTTPException(
            status_code=400, detail="No copies of the book are available to issue"
        )

    # Decrease available quantity
    book.quantity -= 1

    # Create new issued book
    issued_book = models.IssuedBook(
        student_id=student.id,
        book_id=book.id,
        issue_date=datetime.utcnow(),
        due_date=datetime.utcnow() + timedelta(days=10),
        is_returned=False,
    )

    db.add_all([book, issued_book])
    db.commit()
    db.refresh(issued_book)

    return schemas.IssuedBookResponse(
        id=issued_book.id,
        student_name=student.name,
        book_title=book.title,
        issue_date=issued_book.issue_date,
        due_date=issued_book.due_date,
        return_date=issued_book.return_date,
        is_returned=issued_book.is_returned,
    )


@router.post("/return", response_model=schemas.ReturnIssuedBookResponse)
def return_book(
    return_data: schemas.ReturnBookRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can return books.")

    book = (
        db.query(models.Book)
        .filter(models.Book.title.ilike(return_data.book_title))
        .first()
    )
    if not book:
        raise HTTPException(status_code=404, detail="Book not found.")

    issued_book = (
        db.query(models.IssuedBook)
        .filter(
            models.IssuedBook.book_id == book.id,
            models.IssuedBook.student_id == current_user.id,
        )
        .order_by(models.IssuedBook.issue_date.desc())
        .first()
    )

    if not issued_book:
        raise HTTPException(
            status_code=404,
            detail=f"Issued book record not found for this student. (Book ID: {book.id}, Student ID: {current_user.id})",
        )

    if issued_book.is_returned:
        return schemas.ReturnIssuedBookResponse(
            issued_book_id=issued_book.id,
            student_name=current_user.name,
            book_title=book.title,
            return_date=issued_book.return_date,
            is_returned=issued_book.is_returned,
            message=f"'{book.title}' was already returned on {issued_book.return_date.strftime('%Y-%m-%d %H:%M:%S')}.",
            fine_amount=None,
        )

    issued_book.is_returned = True
    issued_book.return_date = datetime.utcnow()

    book.quantity += 1

    fine_amount = None
    if issued_book.return_date.date() > issued_book.due_date.date():
        late_days = (issued_book.return_date.date() - issued_book.due_date.date()).days
        fine_amount = Decimal(late_days * 10)

        fine = models.Fine(amount=fine_amount, issued_book_id=issued_book.id)
        db.add(fine)

    db.commit()
    db.refresh(issued_book)
    
    return schemas.ReturnIssuedBookResponse(
        issued_book_id=issued_book.id,
        student_name=current_user.name,
        book_title=book.title,
        return_date=issued_book.return_date,
        is_returned=issued_book.is_returned,
        message="Book returned successfully",
        fine_amount=fine_amount,
    )
