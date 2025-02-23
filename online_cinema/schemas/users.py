from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional
from enum import Enum


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"


class UserCreateRequestSchema(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    password: str


class UserUpdateRequestSchema(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, min_length=1)
    last_name: Optional[str] = Field(None, min_length=1)
    avatar: Optional[str] = None
    gender: Optional[Gender] = None
    date_of_birth: Optional[date] = None
    info: Optional[str] = None


class UserUpdateResponseSchema(BaseModel):
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


class UserLoginRequestSchema(BaseModel):
    email: EmailStr
    password: str
