import os
import secrets
from datetime import datetime, timedelta
from typing import List
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from online_cinema.database import get_db


load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY", "your-default-secret-key")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
ALGORITHM = os.getenv("ALGORITHM", "HS256")


security = HTTPBearer()


def generate_secure_token(length: int = 32) -> str:
    return secrets.token_urlsafe(length)


def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=1)):
    to_encode = data.copy()
    expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(days=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Security(security),
):
    from online_cinema.accounts.models import UserModel

    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token: user_id missing")

        try:
            user_id = int(user_id)
        except ValueError:
            raise HTTPException(status_code=401, detail="Invalid token: user_id must be an integer")

        db_gen = get_db()
        db = await anext(db_gen)

        try:
            result = await db.execute(
                select(UserModel)
                .options(selectinload(UserModel.group))
                .filter(UserModel.id == user_id)
            )
            user = result.scalar_one_or_none()

            if user is None:
                raise HTTPException(status_code=401, detail="User not found")

            return user

        finally:
            await db_gen.aclose()

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def require_group(required_groups: List[str]):
    async def group_dependency(user: dict = Depends(get_current_user)):
        if user.group.name not in required_groups:
            raise HTTPException(status_code=403, detail=f"You're not permitted to this action")
        return user
    return group_dependency
