import base64
import logging
import os

from fastapi.testclient import TestClient

from src.app import app
from src.database import db
from src.database_models import Coin, Duty
from src.utils import coin_to_dict, is_valid_uuid

if os.getenv("DB_LOGGING") == "on":
    logging.getLogger("peewee").addHandler(logging.StreamHandler())
    logging.getLogger("peewee").setLevel(logging.DEBUG)

# ------------ create test client ----------------
client = TestClient(app)

test_credentials = "testuser:12345678"
encoded_credentials = base64.b64encode(test_credentials.encode("utf-8")).decode("utf-8")
test_headers = {"Authorization": f"Basic {encoded_credentials}"}

test_admin_credentials = "admin:admin"
encoded_admin_credentials = base64.b64encode(
    test_admin_credentials.encode("utf-8")
).decode("utf-8")
admin_headers = {"Authorization": f"Basic {encoded_admin_credentials}"}

# duties routes


def test_duties_route_returns_12_duties(full_database):
    response = client.get("/api/duties")
    duty_list = response.json()
    assert len(duty_list) == 13


def test_all_duties_have_number_and_description(full_database):
    response = client.get("/api/duties")
    duty_list = response.json()
    for duty in duty_list:
        assert "dutyNumber" in duty
        assert "description" in duty


def test_get_single_duty(full_database):
    response = client.get("/api/duties/6")
    duty_object = response.json()

    assert duty_object["dutyNumber"] == 6
    assert "orchestration" in duty_object["description"]
    assert "cloud" not in duty_object["description"]
    assert type(duty_object) == dict


def test_add_new_duty_user(empty_database):
    assert Duty.select().count() == 0
    client.post(
        "/api/duties",
        json={"duty_number": 1, "description": "Script and code"},
        headers=test_headers,
    )
    assert Duty.select().count() == 0


def test_add_new_duty_admin(empty_database):
    assert Duty.select().count() == 0
    client.post(
        "/api/duties",
        json={"duty_number": 1, "description": "Script and code"},
        headers=admin_headers,
    )
    assert Duty.select().count() == 1
    assert "Script and code" in Duty.get(Duty.duty_number == 1).description


def test_update_duty_user(full_database):
    duty_3 = Duty.get(Duty.duty_number == 3)
    assert "mob programming" in duty_3.description

    response = client.put(
        "/api/duties/3/update",
        json={"description": "Work as part of an agile team"},
        headers=test_headers,
    )

    duty_3 = Duty.get(Duty.duty_number == 3)
    assert "mob programming" in duty_3.description
    assert "agile team" not in duty_3.description
    assert "agile team" not in response.text


def test_update_duty_admin(full_database):
    duty_3 = Duty.get(Duty.duty_number == 3)
    assert "mob programming" in duty_3.description

    response = client.put(
        "/api/duties/3/update",
        json={"description": "Work as part of an agile team"},
        headers=admin_headers,
    )

    duty_3 = Duty.get(Duty.duty_number == 3)
    assert "mob programming" not in duty_3.description
    assert "agile team" in duty_3.description
    assert "agile team" in response.text


def test_duties_cannpt_be_deleted(full_database):
    duty_13 = Duty.get(Duty.duty_number == 13)
    assert "you build it, you run it" in duty_13.description
    response = client.delete("/api/duties/13", headers=test_headers)
    duty_13 = Duty.get(Duty.duty_number == 13)
    assert "you build it, you run it" in duty_13.description
    assert "Error" in response.text
