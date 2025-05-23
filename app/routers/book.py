from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_user
from app.database import get_db


router = APIRouter(prefix="/books", tags=["Books"])


# Helper function
def get_author_and_category_ids(db, author_name: str, category_name: str):
    author = db.query(models.Author).filter(models.Author.name == author_name).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author Not Found")
    
    category = db.query(models.Category).filter(models.Category.name == category_name).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category Npot Found")
    
    return author.id, category.id


@router.post("/", response_model=schemas.BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    author_id, category_id = get_author_and_category_ids(db, book.author_name, book.category_name)

    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can create authors")

    existing = (
        db.query(models.Book).filter(models.Book.title == book.title).first()
    )
    if existing:
        raise HTTPException(
            status_code=400, detail="Books with this title already exists"
        )
    
    new_book = models.Book(
        title=book.title,
        publication_date=book.publication_date,
        quantity=book.quantity,
        author_id=author_id,
        category_id=category_id
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
        category_name=book.category_name
    )


@router.get("/", response_model=List[schemas.BookResponse])
def get_all_books(db: Session = Depends(get_db)):
    books = db.query(models.Book).all()
    result = []
    for book in books:
        result.append(
            schemas.BookResponse(
                id=book.id,
                title=book.title,
                publication_date=book.publication_date,
                quantity=book.quantity,
                author_name=book.author.name,
                category_name=book.category.name
            )
        )
    return result


@router.get("/{book_name}", response_model=schemas.BookResponse)
def get_book(title: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    book = db.query(models.Book).filter(models.Book.title == title).first()

    if not book:
        raise HTTPException(status_code=404, detail="Book Not Found")
    
    return book

