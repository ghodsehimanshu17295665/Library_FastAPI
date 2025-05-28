from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_user
from app.database import get_db
from app.utils.pagination import Pagination


router = APIRouter(prefix="/books", tags=["Books"])


# Helper function
def get_author_and_category_ids(db, author_name: str, category_name: str):
    author = db.query(models.Author).filter(models.Author.name == author_name).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author Not Found")

    category = (
        db.query(models.Category).filter(models.Category.name == category_name).first()
    )
    if not category:
        raise HTTPException(status_code=404, detail="Category Npot Found")

    return author.id, category.id


@router.post(
    "/", response_model=schemas.BookResponse, status_code=status.HTTP_201_CREATED
)
def create_book(
    book: schemas.BookCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    author_id, category_id = get_author_and_category_ids(
        db, book.author_name, book.category_name
    )

    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can create authors")

    existing = db.query(models.Book).filter(models.Book.title == book.title).first()
    if existing:
        raise HTTPException(
            status_code=400, detail="Books with this title already exists"
        )

    new_book = models.Book(
        title=book.title,
        publication_date=book.publication_date,
        quantity=book.quantity,
        author_id=author_id,
        category_id=category_id,
    )
    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    return schemas.BookResponse(
        id=new_book.id,
        title=new_book.title,
        publication_date=new_book.publication_date,
        quantity=new_book.quantity,
        author_name=book.author_name,
        category_name=book.category_name,
    )


@router.get("/", response_model=List[schemas.BookResponse])
def get_all_books(
    db: Session = Depends(get_db),
    pagination: Pagination = Depends()
):
    books = (
        db.query(models.Book)
        .offset(pagination.offset)
        .limit(pagination.limit)
        .all()
    )

    result = [
        schemas.BookResponse(
            id=book.id,
            title=book.title,
            publication_date=book.publication_date,
            quantity=book.quantity,
            author_name=book.author.name,
            category_name=book.category.name,
        )
        for book in books
    ]
    return result


@router.get("/{book_name}", response_model=schemas.BookResponse)
def get_book(
    book_name: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    book = db.query(models.Book).filter(models.Book.title == book_name).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book Not Found")

    return schemas.BookResponse(
        id=book.id,
        title=book.title,
        publication_date=book.publication_date,
        quantity=book.quantity,
        author_name=book.author.name,
        category_name=book.category.name,
    )


@router.put("/{book_name}", response_model=schemas.BookUpdate)
def update_book(
    book_name: str,
    update_book: schemas.BookUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can update Books")

    book = db.query(models.Book).filter(models.Book.title == book_name).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if update_book.title:
        book.title = update_book.title
    if update_book.publication_date:
        book.publication_date = update_book.publication_date
    if update_book.quantity:
        book.quantity = update_book.quantity
    if update_book.author_name:
        author = (
            db.query(models.Author)
            .filter(models.Author.name == update_book.author_name)
            .first()
        )
        if not author:
            raise HTTPException(status_code=404, detail="Author Not Found")
        book.author_id = author.id
    if update_book.category_name:
        category = (
            db.query(models.Category)
            .filter(models.Category.name == update_book.category_name)
            .first()
        )
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        book.category_id = category.id

    db.commit()
    db.refresh(book)

    return schemas.BookResponse(
        id=book.id,
        title=book.title,
        publication_date=book.publication_date,
        quantity=book.quantity,
        author_name=book.author.name,
        category_name=book.category.name,
    )


@router.delete("/{book_name}")
def delete_book(
    book_name=str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can Delete Books")

    book = db.query(models.Book).filter(models.Book.title == book_name).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    db.delete(book)
    db.commit()
    return {"message": "Book Deleted Successfully!"}
