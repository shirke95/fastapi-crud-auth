from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from .database import get_db
from .models import Tutorial
from .schemas import TutorialCreate, TutorialUpdate, TutorialPatch
from .auth import get_current_user

router = APIRouter(
    prefix="/tutorials",
    tags=["Tutorials"],
)


@router.post("/")
def create(
    tutorial: TutorialCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    obj = Tutorial(**tutorial.model_dump())

    db.add(obj)
    db.commit()
    db.refresh(obj)

    return obj


@router.get("/")
def get_all(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return db.query(Tutorial).all()


@router.get("/{id}")
def get_one(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    tutorial = db.query(Tutorial).filter(Tutorial.id == id).first()

    if not tutorial:
        raise HTTPException(404, "Tutorial not found")

    return tutorial


@router.put("/{id}")
def update(
    id: int,
    data: TutorialUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    tutorial = db.query(Tutorial).filter(Tutorial.id == id).first()

    if not tutorial:
        raise HTTPException(404, "Tutorial not found")

    tutorial.name = data.name
    tutorial.author = data.author
    tutorial.description = data.description

    db.commit()
    db.refresh(tutorial)

    return tutorial


@router.delete("/{id}")
def delete(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    tutorial = db.query(Tutorial).filter(Tutorial.id == id).first()

    if not tutorial:
        raise HTTPException(404, "Tutorial not found")

    db.delete(tutorial)
    db.commit()

    return {"message": "Deleted"}


@router.patch("/{tutorial_id}")
def patch_tutorial(
    tutorial_id: int,
    request: TutorialPatch,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    tutorial = db.query(Tutorial).filter(Tutorial.id == tutorial_id).first()

    if not tutorial:
        raise HTTPException(404, "Tutorial not found")

    update_data = request.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(tutorial, key, value)

    db.commit()
    db.refresh(tutorial)

    return tutorial
