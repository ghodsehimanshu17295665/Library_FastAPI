from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import database, models, schemas
from app.auth import Hash, create_access_token, get_current_user
from app.utils.email_service import send_email


router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    hashed_pw = Hash.hash_password(user.password)
    # Create new user
    new_user = models.User(
        name=user.name,
        email=user.email,
        password=hashed_pw,
        role=user.role,
        enroll_number=user.enroll_number,
        mobile_number=user.mobile_number,
        gender=user.gender,
        course_id=user.course_id,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    # Send email after registration
    send_email(
        to_email=user.email,
        subject="Library Registration Successful",
        body=f"Hello {user.name},\n\nWelcome to the Library System! Your registration was successful."
    )
    return new_user


@router.get("/all", response_model=List[schemas.UserResponse])
def get_all_users(db: Session = Depends(database.get_db)):
    users = db.query(models.User).all()
    return users


@router.post("/login")
def login(request: schemas.UserLogin, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.email == request.email).first()
    if not db_user or not Hash.verify_password(db_user.password, request.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": db_user.email})
    send_email(
        to_email=db_user.email,
        subject="Library Login Notification",
        body=f"Hello {db_user.name},\n\nYou have successfully logged in to the Library System."
    )
    return {"access_token": token, "token_type": "bearer"}


@router.put("/update-profile", response_model=schemas.UserResponse)
def update_own_profile(
    updated_data: schemas.UserUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),
):
    user_query = db.query(models.User).filter(models.User.email == current_user.email)
    user = user_query.first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_dict = updated_data.dict(exclude_unset=True)

    # Hash password if being updated
    if "password" in update_dict:
        update_dict["password"] = Hash.hash_password(update_dict["password"])

    user_query.update(update_dict)
    db.commit()
    db.refresh(user)

    return user


@router.delete("/delete-profile")
def delete_own_profile(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),
):

    # Only allow student to delete their own profile
    if current_user.role != "student":
        raise HTTPException(
            status_code=403, detail="Only students are allowed to delete their profile"
        )

    user_query = db.query(models.User).filter(models.User.email == current_user.email)
    user = user_query.first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_query.delete()
    db.commit()

    return {"message": f"Student account ({current_user.email}) deleted successfully"}


@router.post("/logout")
def logout(current_user: models.User = Depends(get_current_user)):
    # No action needed for JWT logout on server unless using token blacklist
    return {"message": f"User {current_user.email} logged out successfully"}
