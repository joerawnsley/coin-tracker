import os

import jwt
import pytest
from argon2 import PasswordHasher
from fastapi import HTTPException

from src.auth import get_user_from_token, get_user_from_username
from src.database_models import User
from src.routers.coins_ui import login

ph = PasswordHasher()


def test_get_user_returns_correct_type(full_database):
    user_in_db = get_user_from_username("joe")
    assert isinstance(user_in_db, User)


def test_get_user_returns_correct_data(full_database):
    user_in_db = get_user_from_username("joe")
    ph.verify(user_in_db.hashed_password, "secret")
    assert user_in_db.username == "joe"
    assert user_in_db.role == "user"


def test_get_user_from_token(mocker):
    mocker.patch(
        "jwt.decode",
        return_value={"sub": "joe"},
    )
    user = get_user_from_token("joe")
    assert user.username == "joe"
    assert user.role == "user"


def test_get_current_user_not_exists(mocker):
    mocker.patch("jwt.decode", return_value=None)

    with pytest.raises(HTTPException):
        get_user_from_token("alice")


def test_login_converts_form_submission_to_token(full_database):
    response = login(username="joe", password="secret")
    set_cookie_header = jwt.decode(
        response.headers.get("set-cookie"),
        os.getenv("JWT_SECRET"),
        algorithms=["HS256"],
    )
    assert response.status_code == 303
    assert set_cookie_header.get("sub") == "joe"
