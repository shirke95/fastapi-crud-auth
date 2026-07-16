from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .auth import create_access_token, get_current_user, hash_password, verify_password
from .database import get_db
from .models import User
from .schemas import UserCreate, UserLogin, UserUpdate, UserPatch

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


# ----------------------------
# Register
# ----------------------------
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):

    existing = db.query(User).filter(User.email == user.email).first()

    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = User(
        email=user.email,
        password=hash_password(user.password),
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


# ----------------------------
# Login
# ----------------------------
# @router.post("/login")
# def login(user: UserLogin, db: Session = Depends(get_db)):

#     db_user = db.query(User).filter(User.email == user.email).first()

#     if not db_user:
#         raise HTTPException(401, "Invalid email or password")

#     if not verify_password(user.password, db_user.password):
#         raise HTTPException(401, "Invalid email or password")

#     token = create_access_token(
#         {
#             "sub": db_user.email,
#             "id": db_user.id,
#         }
#     )


#     return {
#         "access_token": token,
#         "token_type": "bearer",
#     }
@router.post("/login")
def login(
    # user: UserLogin,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):

    db_user = db.query(User).filter(User.email == form_data.username).first()

    if not db_user:
        raise HTTPException(401, "Invalid Credentials")

    if not verify_password(
        form_data.password,
        db_user.password,
    ):
        raise HTTPException(401, "Invalid Credentials")

    token = create_access_token(
        {
            "sub": db_user.email,
            "id": db_user.id,
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }


# ----------------------------
# Current User
# ----------------------------
@router.get("/me")
def get_profile(current_user=Depends(get_current_user)):
    return current_user


# ----------------------------
# Get All Users
# ----------------------------
@router.get("/")
def get_users(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    return db.query(User).all()


# ----------------------------
# Get User By ID
# ----------------------------
@router.get("/{user_id}")
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(404, "User not found")

    return user


# ----------------------------
# Update User
# ----------------------------
@router.put("/{user_id}")
def update_user(
    user_id: int,
    request: UserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(404, "User not found")

    # Check duplicate email
    existing = (
        db.query(User).filter(User.email == request.email, User.id != user_id).first()
    )

    if existing:
        raise HTTPException(400, "Email already exists")

    user.email = request.email

    if request.password:
        user.password = hash_password(request.password)

    db.commit()
    db.refresh(user)

    return user


# ----------------------------
# Delete User
# ----------------------------
@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(404, "User not found")

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}


# ----------------------------
# Patch User
# ---------------------------
@router.patch("/{user_id}")
def patch_user(
    user_id: int,
    request: UserPatch,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(404, "User not found")

    update_data = request.model_dump(exclude_unset=True)

    # Check email uniqueness
    if "email" in update_data:
        existing = (
            db.query(User)
            .filter(
                User.email == update_data["email"],
                User.id != user_id,
            )
            .first()
        )

        if existing:
            raise HTTPException(400, "Email already exists")

    # Hash password if updating
    if "password" in update_data:
        update_data["password"] = hash_password(update_data["password"])

    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)

    return user
