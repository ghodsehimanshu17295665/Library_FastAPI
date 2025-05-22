from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_user
from app.database import get_db

router = APIRouter(prefix="/authors", tags=["Authors"])


# Create Author with duplicate email check - Admin Only
@router.post(
    "/", response_model=schemas.AuthorResponse, status_code=status.HTTP_201_CREATED
)
def create_author(
    author: schemas.AuthorCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can create authors")

    existing = (
        db.query(models.Author).filter(models.Author.email == author.email).first()
    )
    if existing:
        raise HTTPException(
            status_code=400, detail="Author with this email already exists"
        )

    db_author = models.Author(**author.dict())
    db.add(db_author)
    db.commit()
    db.refresh(db_author)
    return db_author


# Get All Authors - Student & Admin
@router.get("/", response_model=List[schemas.AuthorResponse])
def get_authors(
    db: Session = Depends(get_db),
):
    return db.query(models.Author).all()


# Get One Author by Email - Admin Only
@router.get("/by-email/{email}", response_model=schemas.AuthorResponse)
def get_author_by_email(
    email: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403, detail="Only admin can get a specific author"
        )

    author = db.query(models.Author).filter(models.Author.email == email).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return author


# Update Author by Email - Admin Only
@router.put("/by-email/{email}", response_model=schemas.AuthorResponse)
def update_author_by_email(
    email: str,
    updated_data: schemas.AuthorCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can update authors")

    author = db.query(models.Author).filter(models.Author.email == email).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    for field, value in updated_data.dict().items():
        setattr(author, field, value)

    db.commit()
    db.refresh(author)
    return author


#  Delete Author by Email - Admin Only
@router.delete("/by-email/{email}", status_code=status.HTTP_204_NO_CONTENT)
def delete_author_by_email(
    email: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can delete authors")

    author = db.query(models.Author).filter(models.Author.email == email).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    db.delete(author)
    db.commit()
    return {"message": f"Author ({author.email}) deleted successfully"}
