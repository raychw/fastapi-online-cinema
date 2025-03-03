from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import date
from typing import Optional
from enum import Enum

from utils.passwords import validate_password_strength, check_password_match


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"


class UserCreateRequestSchema(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    confirm_password: str

    @field_validator("password")
    def validate_password(cls, value):
        return validate_password_strength(value)

    @field_validator("confirm_password")
    def passwords_match(cls, value, info):
        if "password" in info.data:
            return check_password_match(info.data["password"], value)
        return value


class UserCreateResponseSchema(BaseModel):
    message: str


class UserLoginRequestSchema(BaseModel):
    email: EmailStr
    password: str


class UserLoginResponseSchema(BaseModel):
    access_token: str
    refresh_token: str


class UserLogoutRequestSchema(BaseModel):
    pass


class UserLogoutResponseSchema(BaseModel):
    message: str


class UserResetPasswordRequestSchema(BaseModel):
    email: EmailStr


class UserResetPasswordResponseSchema(BaseModel):
    message: str


class UserSetPasswordRequestSchema(BaseModel):
    new_password: str = Field(..., min_length=8)
    confirm_password: str

    @field_validator("new_password")
    def password_strength(cls, password: str):
        return validate_password_strength(password)


class UserSetPasswordResponseSchema(BaseModel):
    message: str


class UserTokenRefreshRequestSchema(BaseModel):
    refresh_token: str


class UserTokenRefreshResponseSchema(BaseModel):
    access_token: str
    refresh_token: str


class UserGetProfileResponseSchema(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    avatar: str
    gender: Gender
    date_of_birth: date
    info: str


class UserUpdateProfileRequestSchema(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, min_length=1)
    last_name: Optional[str] = Field(None, min_length=1)
    avatar: Optional[str] = None
    gender: Optional[Gender] = None
    date_of_birth: Optional[date] = None
    info: Optional[str] = None


class UserUpdateProfileResponseSchema(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    avatar: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    info: Optional[str] = None

    class Config:
        orm_mode = True


class UserActivateRequestSchema(BaseModel):
    email: EmailStr


class UserActivateResponseSchema(BaseModel):
    message: str


class UserChangePasswordRequestSchema(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str

    @field_validator("new_password")
    def password_strength(cls, password: str):
        return validate_password_strength(password)

    @field_validator("confirm_password")
    def passwords_match(cls, value, info):
        if "new_password" in info.data:
            return check_password_match(info.data["new_password"], value)
        return value


class UserChangePasswordResponseSchema(BaseModel):
    message: str
