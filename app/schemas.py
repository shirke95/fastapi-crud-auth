from pydantic import BaseModel, EmailStr, ConfigDict

# =====================================================
# Common Response
# =====================================================


class MessageResponse(BaseModel):
    message: str


# =====================================================
# User Schemas
# =====================================================


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    email: EmailStr


class UserPatch(BaseModel):
    email: EmailStr | None = None


class ChangePassword(BaseModel):
    old_password: str
    new_password: str


class UserRoleUpdate(BaseModel):
    role: str


# =====================================================
# User Response Schemas
# =====================================================


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: str

    model_config = ConfigDict(from_attributes=True)


class UserProfile(UserResponse):
    pass


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


# =====================================================
# Tutorial Schemas
# =====================================================


class TutorialCreate(BaseModel):
    title: str
    description: str
    published: int = 1


class TutorialUpdate(BaseModel):
    title: str
    description: str
    published: int


class TutorialPatch(BaseModel):
    title: str | None = None
    description: str | None = None
    published: int | None = None


# =====================================================
# Tutorial Response
# =====================================================


class TutorialResponse(BaseModel):
    id: int
    title: str
    description: str
    published: int

    model_config = ConfigDict(from_attributes=True)
