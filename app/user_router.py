from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .database import get_db
from .models import User

from .auth import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
    user_access,
    manager_access,
    admin_access,
    get_user_or_404,
    validate_unique_email,
    can_modify_user,
)

from .schemas import (
    UserCreate,
    UserUpdate,
    UserPatch,
    UserRoleUpdate,
    ChangePassword,
    UserProfile,
    UserResponse,
    LoginResponse,
    MessageResponse,
)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: UserCreate,
    db: Session = Depends(get_db),
):
    # Check duplicate email
    validate_unique_email(
        db=db,
        email=request.email,
    )

    # Create user
    user = User(
        email=request.email,
        password=hash_password(request.password),
        role="user",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Login User",
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # Find user by email
    user = db.query(User).filter(User.email == form_data.username).first()

    # Validate credentials
    if not user or not verify_password(
        form_data.password,
        user.password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Generate JWT
    access_token = create_access_token(
        {
            "sub": user.email,
            "id": user.id,
            "role": user.role,
        }
    )

    # Response
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=user,
    )


@router.get(
    "/me",
    response_model=UserProfile,
)
def get_current_user_profile(
    current_user: User = user_access,
):
    """
    Get logged-in user's profile.
    """

    return current_user


@router.patch(
    "/me/password",
    response_model=MessageResponse,
)
def change_password(
    request: ChangePassword,
    db: Session = Depends(get_db),
    current_user: User = user_access,
):
    # Verify old password
    if not verify_password(
        request.old_password,
        current_user.password,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Old password is incorrect",
        )

    # Prevent same password
    if request.old_password == request.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password cannot be the same as old password",
        )

    # (Optional) Validate password length
    if len(request.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long",
        )

    # Hash new password
    current_user.password = hash_password(request.new_password)

    db.commit()

    return {"message": "Password changed successfully"}


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = get_user_or_404(db, user_id)

    # User can view only their own profile
    if current_user.role == "user" and current_user.id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )

    return user


@router.get(
    "/",
    response_model=list[UserResponse],
)
def get_users(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = manager_access,
):
    return db.query(User).offset(skip).limit(limit).all()


@router.put(
    "/{user_id}",
    response_model=UserResponse,
)
def update_user(
    user_id: int,
    request: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Get target user
    user = get_user_or_404(db, user_id)

    # Permission check
    can_modify_user(
        current_user=current_user,
        target_user=user,
    )

    # Check duplicate email
    validate_unique_email(
        db=db,
        email=request.email,
        exclude_user_id=user_id,
    )

    # Update fields
    user.email = request.email

    db.commit()
    db.refresh(user)

    return user


@router.patch(
    "/{user_id}",
    response_model=UserProfile,
)
def patch_user(
    user_id: int,
    request: UserPatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Get user or raise 404
    user = get_user_or_404(db, user_id)

    # RBAC
    # User    -> can update only own profile
    # Manager -> can update any user
    # Admin   -> can update any user
    can_modify_user(
        current_user=current_user,
        target_user=user,
    )

    update_data = request.model_dump(exclude_unset=True)

    # Check email uniqueness
    if "email" in update_data:
        validate_unique_email(
            db=db,
            email=update_data["email"],
            exclude_user_id=user.id,
        )

    # Update fields
    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)

    return user


@router.patch(
    "/me",
    response_model=UserResponse,
)
def update_my_profile(
    request: UserPatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    update_data = request.model_dump(exclude_unset=True)

    # Nothing to update
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided",
        )

    # Check email uniqueness
    if "email" in update_data:
        validate_unique_email(
            db=db,
            email=update_data["email"],
            exclude_user_id=current_user.id,
        )

    # Update fields
    for key, value in update_data.items():
        setattr(current_user, key, value)

    db.commit()
    db.refresh(current_user)

    return current_user


@router.patch(
    "/{user_id}/role",
    response_model=UserResponse,
)
def change_role(
    user_id: int,
    request: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = admin_access,
):

    user = get_user_or_404(
        db,
        user_id,
    )

    allowed_roles = [
        "user",
        "manager",
        "admin",
    ]

    if request.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role",
        )

    # Optional security:
    # Prevent admin from removing own admin access
    if current_user.id == user.id and request.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot remove your own admin access",
        )

    user.role = request.role

    db.commit()
    db.refresh(user)

    return user


@router.delete(
    "/{user_id}",
    response_model=MessageResponse,
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = admin_access,
):

    user = get_user_or_404(
        db,
        user_id,
    )

    # Optional: Prevent admin deleting himself
    if user.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Admin cannot delete own account",
        )

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}
