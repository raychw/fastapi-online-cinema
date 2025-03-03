from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from database import get_db
from schemas.users import (
    UserCreateRequestSchema,
    UserCreateResponseSchema,
    UserLoginRequestSchema,
    UserLoginResponseSchema,
)


router = APIRouter()


@router.post(
    "/register/",
    summary="User registration",
    description="Register a new user with an email and password",
    response_model=UserCreateResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
        user_data: UserCreateRequestSchema,
        db: Session = Depends(get_db)
):
    pass


@router.post(
    "/login/",
    summary="User login",
    description="Sign in user account with an email and password, and receive JWT tokens",
    response_model=UserLoginResponseSchema,
    status_code=status.HTTP_200_OK,
)
def user_login(
        user_data: UserLoginRequestSchema,
        db: Session = Depends(get_db)
):
    pass


@router.post(
    "/logout/",
    summary="User logout",
    description="Sign out of user account and delete JWT token",
    status_code=status.HTTP_200_OK,
)
def user_logout():
    pass


@router.post(
    "/forgot_password/",
    summary="Reset user password",
    description="Send a confirmation email with a reset token to the user",
    status_code=status.HTTP_200_OK,
)
def reset_user_password():
    pass


@router.post(
    "/set_new_password/",
    summary="Set new password",
    description="Set a new password for the user with the reset token",
    status_code=status.HTTP_200_OK,
)
def set_new_password():
    pass


@router.post(
    "/token_refresh/",
    summary="Refresh token",
    description="Refresh access token with refresh token",
    status_code=status.HTTP_200_OK,
)
def refresh_token():
    pass


@router.get(
    "/profile/",
    summary="User profile",
    description="Get user profile information",
    status_code=status.HTTP_200_OK,
)
def user_profile():
    pass


@router.post(
    "/profile/activate/",
    summary="Activate user",
    description="Send a confirmation email to activate the user account",
    status_code=status.HTTP_200_OK,
)
def activate_user():
    pass


@router.post(
    "/profile/update/",
    summary="Update user profile",
    description="Update user profile information",
    status_code=status.HTTP_200_OK,
)
def update_user_profile():
    pass


@router.post(
    "/profile/change_password/",
    summary="Change user password",
    description="Change user password if the old password is correct",
)
def change_user_password():
    pass
