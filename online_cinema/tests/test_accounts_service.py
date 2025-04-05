import pytest
from httpx import ASGITransport, AsyncClient

from online_cinema.main import app
from online_cinema.accounts.models import UserModel as User
from online_cinema.database import SessionLocal


@pytest.fixture
async def user_list():
    async with SessionLocal() as session:
        users = [
            User(id=1, email="alice@example.com", group_id=1, _hashed_password="hashedpassword1"),
            User(id=2, email="bob@example.com", group_id=1, _hashed_password="hashedpassword2"),
        ]
        session.add_all(users)
        await session.commit()

        yield users

        for user in users:
            await session.delete(user)
        await session.commit()


@pytest.mark.anyio
async def test_get_users_list(user_list):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("api/v1/accounts/")
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == len(user_list)
    for user in user_list:
        assert any(u["id"] == user.id and u["email"] == user.email for u in response_json)
