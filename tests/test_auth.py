"""Unit tests for the /auth router and user token flow."""
from fastapi_fundamentals.schemas import User


def _seed_user(session, username="alice", password="secret123") -> User:
    user = User(username=username)
    user.set_password(password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


class TestLogin:
    def test_login_success_returns_token(self, client, session):
        _seed_user(session, username="alice", password="secret123")
        response = client.post(
            "/auth/token",
            data={"username": "alice", "password": "secret123"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["access_token"] == "alice"
        assert body["token_type"] == "bearer"

    def test_login_wrong_password(self, client, session):
        _seed_user(session, username="alice", password="secret123")
        response = client.post(
            "/auth/token",
            data={"username": "alice", "password": "wrong"},
        )
        assert response.status_code == 400
        assert "Incorret" in response.json()["detail"]

    def test_login_unknown_user(self, client):
        response = client.post(
            "/auth/token",
            data={"username": "ghost", "password": "whatever"},
        )
        assert response.status_code == 400
