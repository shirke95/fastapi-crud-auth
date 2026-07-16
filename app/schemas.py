from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    email: EmailStr
    password: str | None = None


class UserPatch(BaseModel):
    email: EmailStr | None = None
    password: str | None = None


class TutorialCreate(BaseModel):
    name: str
    author: str
    description: str


class TutorialPatch(BaseModel):
    name: str | None = None
    author: str | None = None
    description: str | None = None


class TutorialUpdate(TutorialCreate):
    pass
