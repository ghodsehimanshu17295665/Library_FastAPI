from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_user
from app.database import get_db
from app.utils.pagination import Pagination


router = APIRouter(prefix="/course", tags=["Courses"])


@router.post(
    "/", response_model=schemas.CourseResponse, status_code=status.HTTP_201_CREATED
)
def create_course(
    course: schemas.CourseCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can create Courses.")

    existing = db.query(models.Course).filter(models.Course.name == course.name).first()
    if existing:
        raise HTTPException(
            status_code=400, detail="Course with this name already exists"
        )

    new_course = models.Course(
        name=course.name, description=course.description, year=course.year
    )
    db.add(new_course)
    db.commit()
    db.refresh(new_course)

    return schemas.CourseResponse(
        id=new_course.id,
        name=new_course.name,
        description=new_course.description,
        year=new_course.year,
    )


@router.get("/", response_model=List[schemas.CourseResponse])
def get_all_course(db: Session = Depends(get_db), pagination: Pagination = Depends()):
    courses = db.query(models.Course).offset(pagination.offset).limit(pagination.limit).all()
    result = [
        schemas.CourseResponse(
            id=course.id,
            name=course.name,
            description=course.description,
            year=course.year,
        )
        for course in courses
    ]
    return result


@router.get("/{course_name}", response_model=schemas.CourseResponse)
def get_course(
    course_name: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):

    course = db.query(models.Course).filter(models.Course.name == course_name).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course Not Found")

    return schemas.CourseResponse(
        id=course.id, name=course.name, description=course.description, year=course.year
    )


@router.put("/{course_name}", response_model=schemas.CourseResponse)
def update_course(
    course_name: str,
    update_course: schemas.CourseUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can update Courses")

    course = db.query(models.Course).filter(models.Course.name == course_name).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    course.name = update_course.name
    course.description = update_course.description
    course.year = update_course.year

    db.commit()
    db.refresh(course)

    return schemas.CourseResponse(
        id=course.id, name=course.name, description=course.description, year=course.year
    )


@router.delete("/{course_name}")
def delete_course(
    course_name=str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can Delete Books")

    course = db.query(models.Course).filter(models.Course.name == course_name).first()
    if not course:
        raise HTTPException(status_code=404, detail="Book not found")

    db.delete(course)
    db.commit()
    return {"message": "Course Deleted Successfully!"}
