from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from starlette import status

from online_cinema.database import get_db
from services.email import (
    send_activation_email,
    send_password_reset_email,
)
from security.utils import (
    create_access_token,
    create_refresh_token,
    get_current_user,
)
from online_cinema.accounts.crud import (
    get_user_by_id,
    get_list_of_users,
    get_user_by_email,
    create_user,
)
from online_cinema.accounts.models import (
    RefreshTokenModel,
    UserModel,
    PasswordResetTokenModel,
)
from online_cinema.accounts.schemas import (
    UserRegistrationRequestSchema,
    UserRegistrationResponseSchema,
    UserLoginResponseSchema,
    UserLoginRequestSchema,
    MessageResponseSchema,
    UserActivationRequestSchema,
    ResendActivationRequestSchema,
    TokenRefreshResponseSchema,
    TokenRefreshRequestSchema,
    PasswordResetRequestSchema,
    PasswordResetCompleteRequestSchema,
    PasswordChangeRequestSchema,
    UserAccountResponseSchema,
)


router = APIRouter()


@router.post(
    "/register/",
    response_model=UserRegistrationResponseSchema,
    summary="Register a new user",
    description="Register a new user and send a verification email.",
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {
            "description": "Conflict - User with this email already exists.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "A user with this email already exists."
                    }
                }
            },
        },
        500: {
            "description": "Internal Server Error - An error occurred during user creation.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An error occurred during user creation."
                    }
                }
            },
        },
    }
)
async def register_user(
        user_data: UserRegistrationRequestSchema,
        db: AsyncSession = Depends(get_db),
) -> UserRegistrationResponseSchema:
    """
    Endpoint for user registration.

    Validates user password and email. Hashes the password and stores the user in the database.
    Assigns a user group and generates an activation token.

    Sends a verification email to the user with the activation token.
    """

    existing_user = await get_user_by_email(db, user_data.email)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists."
        )

    try:
        new_user = await create_user(db, user_data.model_dump())
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    else:
        return UserRegistrationResponseSchema(
            id=new_user.id,
            email=new_user.email,
        )


@router.post(
    "/activate/",
    response_model=MessageResponseSchema,
    summary="Activate a user account",
    description="Activate a user account using the token sent to their email.",
    status_code=status.HTTP_200_OK,
    responses={
        400: {
            "description": "Bad Request - Invalid token or email.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid token or email."
                    }
                }
            },
        },
        500: {
            "description": "Internal Server Error - An error occurred during activation.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An error occurred during activation."
                    }
                }
            },
        },
    }
)
async def activate_user(
        user_data: UserActivationRequestSchema,
        db: AsyncSession = Depends(get_db),
):
    """
    Endpoint for user account activation.

    Validates the activation token and email. If valid, activates the user account.
    """

    user = await get_user_by_email(db, user_data.email)

    await db.refresh(user, ["activation_token"])

    if not user or user_data.token != user.activation_token.token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token or email."
        )

    try:
        user.is_active = True
        db.add(user)
        await db.flush()
        await db.commit()

        return MessageResponseSchema(message="User account activated successfully.")
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/resend-verification/",
    response_model=MessageResponseSchema,
    summary="Resend verification email",
    description="Resend the verification email to the user.",
    status_code=status.HTTP_200_OK,
    responses={
        400: {
            "description": "Bad Request - Invalid email.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid email."
                    }
                }
            },
        },
        500: {
            "description": "Internal Server Error - An error occurred during email sending.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An error occurred during email sending."
                    }
                }
            },
        },
    }
)
async def resend_activation(
        user_data: ResendActivationRequestSchema,
        db: AsyncSession = Depends(get_db),
):
    """
    Endpoint to resend the activation email.

    Validates the email and checks if the user exists. If valid, sends a new activation email.
    """

    existent_user = await get_user_by_email(db, user_data.email)

    if not existent_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email."
        )

    try:
        send_activation_email(str(user_data.email), existent_user.activation_token.token)
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    else:
        return MessageResponseSchema(message="If the email is correct, "
                                             "you will find a verification email in your inbox.")


@router.post(
    "/login/",
    response_model=UserLoginResponseSchema,
    summary="Log in a user",
    description="Log in a user and issue them access and refresh JWT tokens.",
    status_code=status.HTTP_200_OK,
    responses={
        401: {
            "description": "Unauthorized - Invalid credentials.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid credentials."
                    }
                }
            },
        },
        403: {
            "description": "Forbidden - User is inactive.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "User account is not activated."
                    }
                }
            },
        },
        500: {
            "description": "Internal Server Error - An error occurred during login.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An error occurred during login."
                    }
                }
            },
        },
    }
)
async def login_user(
        user_data: UserLoginRequestSchema,
        db: AsyncSession = Depends(get_db),
):
    """
    Endpoint for user login.

    Validates user credentials (email and password). If valid, issues access and refresh JWT tokens.
    """

    user = await get_user_by_email(db, user_data.email)

    if not user or not user.verify_password(user_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not activated."
        )

    try:
        jwt_refresh_token = create_refresh_token(
        {
            "sub": user.email,
            "user_id": user.id
        }
        )

        new_refresh_token = RefreshTokenModel.create(
            user_id=user.id,
            days_valid=30,
            token=jwt_refresh_token,
        )
        db.add(new_refresh_token)
        await db.flush()
        await db.commit()

        jwt_access_token = create_access_token(
            {
                "sub": user.email,
                "user_id": user.id
            }
        )

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    else:
        return UserLoginResponseSchema(
            access_token=jwt_access_token,
            refresh_token=jwt_refresh_token,
        )


@router.post(
    "/refresh-token/",
    response_model=TokenRefreshResponseSchema,
    summary="Refresh access token",
    description="Refresh the access token using the refresh token.",
    status_code=status.HTTP_200_OK,
    responses={
        401: {
            "description": "Unauthorized - Invalid refresh token.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid refresh token."
                    }
                }
            },
        },
        403: {
            "description": "Forbidden - Refresh token is expired or revoked.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Refresh token is expired or revoked."
                    }
                }
            },
        },
        500: {
            "description": "Internal Server Error - An error occurred during token refresh.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An error occurred during token refresh."
                    }
                }
            },
        },
    }
)
async def refresh_token(
        token_data: TokenRefreshRequestSchema,
        db: AsyncSession = Depends(get_db),
):
    """
    Endpoint for refreshing user access JWT token.

    Validates the refresh token and issues a new access token.
    """

    try:
        jwt_refresh_token = await db.execute(
            select(RefreshTokenModel).where(RefreshTokenModel.token == token_data.refresh_token)
        )
        jwt_refresh_token = jwt_refresh_token.scalars().first()

        if not jwt_refresh_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token.")

        if jwt_refresh_token.expires_at < datetime.now():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Refresh token is expired or revoked.")

        user = await db.execute(
            select(UserModel).where(UserModel.id == jwt_refresh_token.user_id)
        )
        user = user.scalars().first()

        if not user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not found.")

        new_access_token = create_access_token({"sub": user.email})

        return TokenRefreshResponseSchema(
            access_token=new_access_token,
            token_type="bearer"
        )
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/logout/",
    response_model=MessageResponseSchema,
    summary="Log out a user",
    description="Log out a user and revoke their access and refresh tokens.",
    status_code=status.HTTP_200_OK,
    responses={
        500: {
            "description": "Internal Server Error - An error occurred during logout.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An error occurred during logout."
                    }
                }
            },
        },
    }
)
async def logout_user(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Endpoint for user logout.
    Logs out the user and revokes their access and refresh tokens.
    """
    try:
        await db.execute(
            delete(RefreshTokenModel).where(RefreshTokenModel.user_id == user["user_id"])
        )
        await db.commit()
        return MessageResponseSchema(message="User logged out successfully")
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/reset-password/",
    response_model=MessageResponseSchema,
    summary="Reset user password",
    description="Send a password reset email to the user.",
    status_code=status.HTTP_200_OK,
    responses={
        400: {
            "description": "Bad Request - Invalid email.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid email."
                    }
                }
            },
        },
        500: {
            "description": "Internal Server Error - An error occurred during password reset.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An error occurred during password reset."
                    }
                }
            },
        },
    }
)
async def reset_password(
        user_data: PasswordResetRequestSchema,
        db: AsyncSession = Depends(get_db),
):
    """
    Send a password reset email to the user with a password reset token.
    """

    user = await get_user_by_email(db, user_data.email)

    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    try:
        password_reset_token = PasswordResetTokenModel(user_id=user.id)
        db.add(password_reset_token)

        await db.flush()
        await db.commit()
        await db.refresh(password_reset_token)

        send_password_reset_email(str(user_data.email), password_reset_token.token)
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    else:
        return MessageResponseSchema(message="If the email is correct, you'll get a password reset token.")


@router.post(
    "/set-new-password/",
    response_model=MessageResponseSchema,
    summary="Set a new password",
    description="Set a new password for the user using the reset token.",
    status_code=status.HTTP_200_OK,
    responses={
        400: {
            "description": "Bad Request - Invalid token.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid token."
                    }
                }
            },
        },
        500: {
            "description": "Internal Server Error - An error occurred during password reset.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An error occurred during password reset."
                    }
                }
            },
        },
    }
)
async def set_new_password(
        user_data: PasswordResetCompleteRequestSchema,
        db: AsyncSession = Depends(get_db),
):
    """
    Set a new password for the user using the reset token.
    """

    user = await db.execute(
        select(UserModel).where(UserModel.password_reset_token.has(PasswordResetTokenModel.token == user_data.token))
    )
    user = user.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    try:
        user.password = user_data.password
        db.add(user)
        await db.flush()
        await db.commit()

        return MessageResponseSchema(message="New password was set successfully. You may now log in.")
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/change-password/",
    response_model=MessageResponseSchema,
    summary="Change user password",
    description="Change the user's password if the old one is correct.",
    status_code=status.HTTP_200_OK,
    responses={
        400: {
            "description": "Bad Request - Invalid password.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid password."
                    }
                }
            },
        },
        500: {
            "description": "Internal Server Error - An error occurred during password change.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An error occurred during password change."
                    }
                }
            },
        },
    }
)
async def change_password(
    user_data: PasswordChangeRequestSchema,
    db: AsyncSession = Depends(get_db),
):
    """
    Change a user's password.
    """

    user = await db.execute(
        select(UserModel).where(UserModel.email == user_data.email)
    )
    user = user.scalars().first()

    if not user.verify_password(user_data.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    try:
        user.password = user_data.new_password
        db.add(user)
        await db.flush()
        await db.commit()

        return MessageResponseSchema(message="Password was changed successfully.")
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/",
    response_model=List[UserAccountResponseSchema],
    summary="Get all users",
    description="Get a list of all users.",
    status_code=status.HTTP_200_OK,
    responses={
        500: {
            "description": "Internal Server Error - An error occurred during fetching users.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An error occurred during fetching users."
                    }
                }
            },
        },
    }
)
async def get_users(
        db: AsyncSession = Depends(get_db),
):
    """
    Get all users list.
    """

    try:
        users = await get_list_of_users(db)
        return [UserAccountResponseSchema.model_validate(user) for user in users]
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/{user_id}/",
    response_model=UserAccountResponseSchema,
    summary="Get user by ID",
    description="Get a user by their ID.",
    status_code=status.HTTP_200_OK,
    responses={
        404: {
            "description": "Not Found - User not found.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "User not found."
                    }
                }
            },
        },
        500: {
            "description": "Internal Server Error - An error occurred during fetching user.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An error occurred during fetching user."
                    }
                }
            },
        },
    }
)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a user by ID.
    """

    user = await get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    try:
        return user
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
