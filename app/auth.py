import jwt

from datetime import datetime, timedelta, timezone

from pwdlib import PasswordHash

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.orm import Session

from .database import get_db
from .models import User

# =====================================================
# JWT Configuration
# =====================================================

SECRET_KEY = "your_super_secret_key_change_this_to_random_string"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

# =====================================================
# Password Helpers
# =====================================================


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


# =====================================================
# JWT Helpers
# =====================================================


def create_access_token(data: dict):

    payload = data.copy()

    payload["exp"] = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def decode_access_token(token: str):

    try:
        return jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

    except jwt.PyJWTError:
        return None


# =====================================================
# Current User
# =====================================================


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):

    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    email = payload["sub"]

    user = db.query(User).filter(User.email == email).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


# =====================================================
# Role Based Access
# =====================================================


def require_roles(*roles):

    def checker(
        current_user: User = Depends(get_current_user),
    ):

        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied",
            )

        return current_user

    return checker


user_access = Depends(
    require_roles(
        "user",
        "manager",
        "admin",
    )
)

manager_access = Depends(
    require_roles(
        "manager",
        "admin",
    )
)

admin_access = Depends(
    require_roles(
        "admin",
    )
)

# =====================================================
# Database Helpers
# =====================================================


def get_user_or_404(
    db: Session,
    user_id: int,
) -> User:

    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


def validate_unique_email(
    db: Session,
    email: str,
    exclude_user_id: int | None = None,
):

    query = db.query(User).filter(User.email == email)

    if exclude_user_id is not None:
        query = query.filter(User.id != exclude_user_id)

    if query.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists",
        )


# =====================================================
# Permission Helpers
# =====================================================


def can_modify_user(
    current_user: User,
    target_user: User,
):
    """
    User    -> can modify only own profile
    Manager -> can modify everyone
    Admin   -> can modify everyone
    """

    if current_user.role in (
        "admin",
        "manager",
    ):
        return

    if current_user.id != target_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )


def can_delete(
    current_user: User,
):
    """
    Only Admin can delete
    """

    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can delete",
        )


# =====================================================
# Role Helpers
# =====================================================


def is_admin(user: User) -> bool:
    return user.role == "admin"


def is_manager(user: User) -> bool:
    return user.role == "manager"


def is_user(user: User) -> bool:
    return user.role == "user"
