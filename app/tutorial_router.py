from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .database import get_db
from .models import Tutorial, User

from .schemas import (
    TutorialCreate,
    TutorialUpdate,
    TutorialPatch,
    TutorialResponse,
    MessageResponse,
)

from .auth import (
    manager_access,
    admin_access,
    user_access,
    get_user_or_404,
)

router = APIRouter(
    prefix="/tutorials",
    tags=["Tutorials"],
)


# =====================================================
# CREATE TUTORIAL
# Manager + Admin
# =====================================================


@router.post(
    "/",
    response_model=TutorialResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_tutorial(
    request: TutorialCreate,
    db: Session = Depends(get_db),
    current_user: User = manager_access,
):

    tutorial = Tutorial(**request.model_dump())

    db.add(tutorial)
    db.commit()
    db.refresh(tutorial)

    return tutorial


# =====================================================
# GET ALL TUTORIALS
# User + Manager + Admin
# =====================================================


@router.get(
    "/",
    response_model=list[TutorialResponse],
)
def get_tutorials(
    db: Session = Depends(get_db),
    current_user: User = user_access,
):

    return db.query(Tutorial).all()


# =====================================================
# GET SINGLE TUTORIAL
# User + Manager + Admin
# =====================================================


@router.get(
    "/{tutorial_id}",
    response_model=TutorialResponse,
)
def get_tutorial(
    tutorial_id: int,
    db: Session = Depends(get_db),
    current_user: User = user_access,
):

    tutorial = db.query(Tutorial).filter(Tutorial.id == tutorial_id).first()

    if tutorial is None:
        raise HTTPException(
            status_code=404,
            detail="Tutorial not found",
        )

    return tutorial


# =====================================================
# UPDATE FULL TUTORIAL
# Manager + Admin
# =====================================================


@router.put(
    "/{tutorial_id}",
    response_model=TutorialResponse,
)
def update_tutorial(
    tutorial_id: int,
    request: TutorialUpdate,
    db: Session = Depends(get_db),
    current_user: User = manager_access,
):

    tutorial = db.query(Tutorial).filter(Tutorial.id == tutorial_id).first()

    if tutorial is None:
        raise HTTPException(
            404,
            "Tutorial not found",
        )

    tutorial.title = request.title
    tutorial.description = request.description
    tutorial.published = request.published

    db.commit()
    db.refresh(tutorial)

    return tutorial


# =====================================================
# PATCH PARTIAL UPDATE
# Manager + Admin
# =====================================================


@router.patch(
    "/{tutorial_id}",
    response_model=TutorialResponse,
)
def patch_tutorial(
    tutorial_id: int,
    request: TutorialPatch,
    db: Session = Depends(get_db),
    current_user: User = manager_access,
):

    tutorial = db.query(Tutorial).filter(Tutorial.id == tutorial_id).first()

    if tutorial is None:
        raise HTTPException(
            404,
            "Tutorial not found",
        )

    update_data = request.model_dump(exclude_unset=True)

    for key, value in update_data.items():

        setattr(
            tutorial,
            key,
            value,
        )

    db.commit()
    db.refresh(tutorial)

    return tutorial


# =====================================================
# DELETE TUTORIAL
# Admin Only
# =====================================================


@router.delete(
    "/{tutorial_id}",
    response_model=MessageResponse,
)
def delete_tutorial(
    tutorial_id: int,
    db: Session = Depends(get_db),
    current_user: User = admin_access,
):

    tutorial = db.query(Tutorial).filter(Tutorial.id == tutorial_id).first()

    if tutorial is None:
        raise HTTPException(
            404,
            "Tutorial not found",
        )

    db.delete(tutorial)
    db.commit()

    return {"message": "Tutorial deleted successfully"}
