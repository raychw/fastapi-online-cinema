from pydantic import BaseModel, EmailStr, field_validator

from online_cinema.security import validators


class BaseEmailPasswordSchema(BaseModel):
    email: EmailStr
    password: str

    model_config = {
        "from_attributes": True
    }

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        return value.lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        return validators.validate_password_strength(value)


class UserRegistrationRequestSchema(BaseEmailPasswordSchema):
    pass


class EmailInputRequestSchema(BaseModel):
    email: EmailStr

    model_config = {
        "from_attributes": True
    }


class ResendActivationRequestSchema(EmailInputRequestSchema):
    pass


class PasswordResetRequestSchema(EmailInputRequestSchema):
    pass


class PasswordResetCompleteRequestSchema(BaseEmailPasswordSchema):
    token: str


class PasswordChangeRequestSchema(BaseEmailPasswordSchema):
    new_password: str


class UserLoginRequestSchema(BaseEmailPasswordSchema):
    pass


class UserLoginResponseSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserRegistrationResponseSchema(BaseModel):
    id: int
    email: EmailStr
    message: str = "User registered successfully. Please check your email to activate your account."

    model_config = {
        "from_attributes": True
    }


class UserActivationRequestSchema(BaseModel):
    email: EmailStr
    token: str


class MessageResponseSchema(BaseModel):
    message: str


class TokenRefreshRequestSchema(BaseModel):
    refresh_token: str


class TokenRefreshResponseSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserAccountResponseSchema(BaseModel):
    id: int
    email: EmailStr
    is_active: bool

    model_config = {
        "from_attributes": True
    }
