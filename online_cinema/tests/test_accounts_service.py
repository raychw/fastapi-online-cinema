import pytest
from datetime import datetime, timedelta
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from online_cinema.main import app
from online_cinema.accounts.models import RefreshTokenModel, ActivationTokenModel, UserModel as User
from online_cinema.database import SessionLocal
from online_cinema.security.passwords import hash_password


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


@pytest.fixture
async def user():
    async with SessionLocal() as session:
        user = User(
            id=1,
            email="joanne@example.com",
            group_id=1,
            _hashed_password=hash_password("strSTR!0"),
            is_active=True,
        )
        session.add(user)
        await session.flush()

        activation_token = ActivationTokenModel(
            user_id=user.id,
        )
        session.add(activation_token)
        await session.commit()
        await session.refresh(user)

        yield user

        await session.delete(user)
        await session.commit()


@pytest.fixture
async def inactive_user():
    async with SessionLocal() as session:
        user = User(
            id=2,
            email="inactive@example.com",
            group_id=1,
            _hashed_password=hash_password("strSTR!0"),
            is_active=False,
        )
        session.add(user)
        await session.flush()

        activation_token = ActivationTokenModel(
            user_id=user.id,
        )
        session.add(activation_token)
        await session.commit()
        await session.refresh(user)

        yield user, activation_token.token

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


@pytest.mark.anyio
async def test_get_user(user):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get(f"api/v1/accounts/{user.id}/")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["id"] == user.id
    assert response_json["email"] == user.email


@pytest.mark.anyio
async def test_register_user():
    new_user_data = {
        "email": "dave@example.com",
        "password": "strSTR!0"
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("api/v1/accounts/register/", json=new_user_data)

    assert response.status_code == 201
    response_json = response.json()
    assert response_json["email"] == new_user_data["email"]
    assert "id" in response_json
    assert "password" not in response_json

    async with SessionLocal() as session:
        new_user = await session.get(User, response_json["id"])
        await session.delete(new_user)
        await session.commit()


@pytest.mark.anyio
async def test_register_user_with_existing_email(user):
    existing_user_data = {
        "email": user.email,
        "password": "strSTR!0"
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("api/v1/accounts/register/", json=existing_user_data)

    assert response.status_code == 409
    response_json = response.json()
    assert response_json["detail"] == "A user with this email already exists."


@pytest.mark.anyio
async def test_activate_user(inactive_user):
    user, token = inactive_user

    activation_data = {
        "email": user.email,
        "token": token,
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("api/v1/accounts/activate/", json=activation_data)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["message"] == "User account activated successfully."

    async with SessionLocal() as session:
        activated_user = await session.get(User, user.id)
        assert activated_user.is_active is True


@pytest.mark.anyio
async def test_activate_user_invalid_data(inactive_user):
    user, token = inactive_user

    invalid_activation_data = {
        "email": user.email,
        "token": "invalid_token",
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("api/v1/accounts/activate/", json=invalid_activation_data)

    assert response.status_code == 400
    response_json = response.json()
    assert response_json["detail"] == "Invalid token or email."

    async with SessionLocal() as session:
        not_activated_user = await session.get(User, user.id)
        assert not_activated_user.is_active is False


@pytest.mark.anyio
async def test_resend_activation_email(inactive_user):
    user, token = inactive_user

    resend_data = {
        "email": user.email,
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("api/v1/accounts/resend-verification/", json=resend_data)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["message"] == ("If the email is correct, "
                                        "you will find a verification email in your inbox.")


@pytest.mark.anyio
async def test_resend_activation_to_invalid_email():
    resend_data = {
        "email": "invalid_email_data@email.com"
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("api/v1/accounts/resend-verification/", json=resend_data)
    assert response.status_code == 400
    response_json = response.json()
    assert response_json["detail"] == "Invalid email or account is already activated."


@pytest.mark.anyio
async def test_user_login(user):
    login_data = {
        "email": user.email,
        "password": "strSTR!0"
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("api/v1/accounts/login/", json=login_data)

    assert response.status_code == 200
    response_json = response.json()
    assert "access_token" in response_json
    assert "token_type" in response_json
    assert response_json["token_type"] == "bearer"


@pytest.mark.anyio
async def test_user_login_with_inactive_account(inactive_user):
    login_data = {
        "email": inactive_user[0].email,
        "password": "strSTR!0"
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("api/v1/accounts/login/", json=login_data)

    assert response.status_code == 403
    response_json = response.json()
    assert response_json["detail"] == "User account is not activated."


@pytest.mark.anyio
async def test_user_login_invalid_credentials(user):
    login_data = {
        "email": user.email,
        "password": "strSTR!1"
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("api/v1/accounts/login/", json=login_data)

    assert response.status_code == 401
    response_json = response.json()
    assert response_json["detail"] == "Invalid credentials."


@pytest.mark.anyio
async def test_refresh_token_success(user):
    login_data = {
        "email": user.email,
        "password": "strSTR!0"
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("api/v1/accounts/login/", json=login_data)

    assert response.status_code == 200
    response_json = response.json()
    refresh_token = response_json["refresh_token"]

    refresh_data = {
        "refresh_token": refresh_token
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("api/v1/accounts/refresh-token/", json=refresh_data)

    assert response.status_code == 200
    response_json = response.json()
    assert "access_token" in response_json
    assert "token_type" in response_json
    assert response_json["token_type"] == "bearer"


@pytest.mark.anyio
async def test_refresh_token_invalid_token(user):
    login_data = {
        "email": user.email,
        "password": "strSTR!0"
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("api/v1/accounts/login/", json=login_data)

    assert response.status_code == 200

    refresh_data = {
        "refresh_token": "invalid_refresh_token"
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("api/v1/accounts/refresh-token/", json=refresh_data)

    assert response.status_code == 401
    response_json = response.json()
    assert response_json["detail"] == "Invalid refresh token."


@pytest.mark.anyio
async def test_refresh_token_expired_token(user):
    login_data = {
        "email": user.email,
        "password": "strSTR!0"
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("api/v1/accounts/login/", json=login_data)

    assert response.status_code == 200
    response_json = response.json()
    refresh_token = response_json["refresh_token"]

    async with SessionLocal() as session:
        result = await session.execute(
            select(RefreshTokenModel).where(RefreshTokenModel.token == refresh_token)
        )
        token_record = result.scalar_one_or_none()

        assert token_record is not None, "Refresh token not found in the database"

        token_record.expires_at = datetime.now() - timedelta(days=1)
        await session.commit()

    refresh_data = {
        "refresh_token": refresh_token
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("api/v1/accounts/refresh-token/", json=refresh_data)

    assert response.status_code == 403
    response_json = response.json()
    assert response_json["detail"] == "Refresh token is expired or revoked."


@pytest.mark.anyio
async def test_logout_user(user):
    login_data = {
        "email": user.email,
        "password": "strSTR!0"
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        login_response = await ac.post("/api/v1/accounts/login/", json=login_data)
        assert login_response.status_code == 200
        tokens = login_response.json()
        assert "access_token" in tokens
        access_token = tokens["access_token"]

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        logout_response = await ac.post(
            "/api/v1/accounts/logout/",
            headers={"Authorization": f"Bearer {access_token}"}
        )

    assert logout_response.status_code == 200
    assert logout_response.json()["message"] == "User logged out successfully"

    async with SessionLocal() as session:
        user = await session.scalar(select(User).where(User.email == login_data["email"]))
        tokens_exist = await session.scalar(
            select(RefreshTokenModel).where(RefreshTokenModel.user_id == user.id)
        )
        assert tokens_exist is None


@pytest.mark.anyio
async def test_reset_password(user):
    reset_data = {
        "email": user.email,
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("api/v1/accounts/reset-password/", json=reset_data)
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["message"] == "If the email is correct, you will find a reset password email in your inbox."

    async with SessionLocal() as session:
        user_in_db = await session.get(User, user.id)
        await session.refresh(user_in_db, ["password_reset_token"])
        assert user_in_db.password_reset_token is not None


@pytest.mark.anyio
async def test_reset_password_invalid_email(user):
    reset_data = {
        "email": "wrongemail@test.com",
    }

    async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("api/v1/accounts/reset-password/", json=reset_data)
    assert response.status_code == 400
    response_json = response.json()
    assert response_json["detail"] == "Invalid email."


@pytest.mark.anyio
async def test_set_new_password(user):
    reset_data = {
        "email": user.email,
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("api/v1/accounts/reset-password/", json=reset_data)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["message"] == "If the email is correct, you will find a reset password email in your inbox."

    async with SessionLocal() as session:

        user = await session.get(User, user.id)
        await session.refresh(user, ["password_reset_token"])

        set_new_password_data = {
            "email": user.email,
            "password": "strSTR!123",
            "token": user.password_reset_token.token,
        }

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            response = await ac.post("api/v1/accounts/set-new-password/", json=set_new_password_data)

        assert response.status_code == 200
        response_json = response.json()
        assert response_json["message"] == "New password was set successfully. You may now log in."


@pytest.mark.anyio
async def test_set_new_password_invalid_token(user):
    reset_data = {
        "email": user.email,
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("api/v1/accounts/reset-password/", json=reset_data)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["message"] == "If the email is correct, you will find a reset password email in your inbox."

    async with SessionLocal() as session:
        user = await session.get(User, user.id)
        await session.refresh(user, ["password_reset_token"])

        set_new_password_data = {
            "email": user.email,
            "password": "strSTR!123",
            "token": "invalid_token",
        }

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            response = await ac.post("api/v1/accounts/set-new-password/", json=set_new_password_data)

        assert response.status_code == 400
        response_json = response.json()
        assert response_json["detail"] == "Invalid token."


@pytest.mark.anyio
async def test_change_password(user):
    login_data = {
        "email": user.email,
        "password": "strSTR!0"
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("api/v1/accounts/login/", json=login_data)

    assert response.status_code == 200

    change_password_data = {
        "email": user.email,
        "password": "strSTR!0",
        "new_password": "new_strSTR!123"
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(
            "api/v1/accounts/change-password/",
            json=change_password_data
        )

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["message"] == "Password was changed successfully."

    login_data["password"] = change_password_data["new_password"]
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("api/v1/accounts/login/", json=login_data)

    assert response.status_code == 200


@pytest.mark.anyio
async def test_change_password_wrong_password(user):
    login_data = {
        "email": user.email,
        "password": "strSTR!0"
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("api/v1/accounts/login/", json=login_data)

    assert response.status_code == 200

    change_password_data = {
        "email": user.email,
        "password": "strSTR!000",
        "new_password": "new_strSTR!123"
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(
            "api/v1/accounts/change-password/",
            json=change_password_data
        )

    assert response.status_code == 400
    response_json = response.json()
    assert response_json["detail"] == "Old password is not correct."
