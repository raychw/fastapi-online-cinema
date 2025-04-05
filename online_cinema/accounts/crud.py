from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from online_cinema.accounts.models import (
    UserModel,
    UserGroupModel,
    UserGroupEnum,
    ActivationTokenModel
)
from online_cinema.services.email import send_activation_email


async def get_user_by_id(db: AsyncSession, user_id: int):
    stmt = select(UserModel).where(UserModel.id == user_id)
    result = await db.execute(stmt)
    return result.scalars().first()


async def get_list_of_users(db: AsyncSession, skip: int = 0, limit: int = 10):
    stmt = select(UserModel).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_user_by_email(db: AsyncSession, email: EmailStr):
    stmt = (
        select(UserModel)
        .options(joinedload(UserModel.activation_token))  # Load relationship eagerly
        .where(UserModel.email == email)
    )
    result = await db.execute(stmt)
    return result.scalars().first()


async def create_user(db: AsyncSession, user_data: dict):
    stmt = select(UserGroupModel).where(UserGroupModel.name == UserGroupEnum.USER)
    result = await db.execute(stmt)
    user_group = result.scalar()

    new_user = UserModel.create(
        email=str(user_data["email"]),
        raw_password=user_data["password"],
        group_id=user_group.id,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    activation_token = ActivationTokenModel(user_id=new_user.id)
    db.add(activation_token)

    await db.commit()
    await db.refresh(activation_token)

    send_activation_email(str(new_user.email), activation_token.token)

    return new_user
