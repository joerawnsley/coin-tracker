from src.auth import User, UserInDB, get_user, get_current_user

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