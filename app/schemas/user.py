from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.enums import PowerEnum


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    introduction: str | None = None


class UserPasswordUpdate(BaseModel):
    old_password: str
    new_password: str


class User(BaseModel):
    id: int
    username: str
    email: EmailStr
    introduction: str | None = None
    avatar: str | None = None
    power: PowerEnum
    model_config = ConfigDict(from_attributes=True)
