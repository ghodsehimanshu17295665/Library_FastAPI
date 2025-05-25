from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_user
from app.database import get_db

router = APIRouter(prefix="/category", tags=["Categories"])


# Create Category - Admin Only
@router.post(
    "/", response_model=schemas.CategoryResponse, status_code=status.HTTP_201_CREATED
)
def create_category(
    category: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can create categories")

    existing = (
        db.query(models.Category).filter(models.Category.name == category.name).first()
    )
    if existing:
        raise HTTPException(
            status_code=400, detail="Category with this name already exists"
        )

    db_category = models.Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


# Get All Categories - Student & Admin
@router.get("/", response_model=List[schemas.CategoryResponse])
def get_categories(
    db: Session = Depends(get_db),
):
    return db.query(models.Category).all()


# Get One Category by Name - Admin Only
@router.get("/by-name/{name}", response_model=schemas.CategoryResponse)
def get_category_by_name(
    name: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403, detail="Only admin can view category by name"
        )

    category = (
        db.query(models.Category).filter(models.Category.name.ilike(name)).first()
    )
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


# Update Category - Admin Only
@router.put("/by-name/{name}", response_model=schemas.CategoryResponse)
def update_category_by_name(
    name: str,
    updated_data: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can update categories")

    category = db.query(models.Category).filter(models.Category.name == name).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    for field, value in updated_data.dict().items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)
    return category


# Delete Category - Admin Only
@router.delete("/by-name/{name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category_by_name(
    name: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can delete categories")

    category = db.query(models.Category).filter(models.Category.name == name).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    db.delete(category)
    db.commit()
    return {"message": "Category Deleted Successfully!"}
