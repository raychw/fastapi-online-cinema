from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from online_cinema.accounts.models import (
    UserModel,
    UserGroupModel,
    UserGroupEnum,
    ActivationTokenModel
)


async def get_user_by_email(db: AsyncSession, email: EmailStr):
    stmt = select(UserModel).where(UserModel.email == email)
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

    return new_user
