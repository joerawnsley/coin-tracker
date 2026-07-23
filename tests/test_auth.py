from src.auth import UserInDB, get_user, get_current_user
from src.routers.auth_api import login
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
import pytest

fake_users_db = {
    "joe": {
        "username": "joe",
        "hashed_password": "fakehashedsecret"
    },
    "admin": {
            "username": "admin",
            "hashed_password": "fakehashedadmin"
    }
}

def test_get_user_returns_correct_type():
    user_in_db = get_user(fake_users_db, "joe")
    assert isinstance(user_in_db, UserInDB)
    
def test_get_user_returns_correct_data():
    user_in_db = get_user(fake_users_db, "joe")
    assert user_in_db.hashed_password == "fakehashedsecret"
    assert user_in_db.username == "joe"
    
def test_get_current_user(mocker):
    mocker.patch("src.auth.decode_token", return_value=UserInDB(
        username="joe",
        hashed_password="fakehashedsecret"
    ))
    user = get_current_user("joe")
    assert user.username == "joe"

def test_get_current_user_not_exists(mocker):
    mocker.patch("src.auth.decode_token", return_value=None)
    
    with pytest.raises(HTTPException):
        get_current_user("alice")

def test_login_converts_form_submission_to_token():
    response = login(username="joe", password='secret')
    set_cookie_header = response.headers.get("set-cookie")
    assert response.status_code == 303
    assert "access_token=" in set_cookie_header
    assert "Bearer joe" in set_cookie_header
    
