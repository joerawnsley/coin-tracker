import logging
import os

import peewee
import pytest

from src.database import db
from src.database_models import Coin, Duty
from src.utils import is_valid_uuid

if os.getenv("DB_LOGGING") == "on":
    logging.getLogger("peewee").addHandler(logging.StreamHandler())
    logging.getLogger("peewee").setLevel(logging.DEBUG)


# -------- connection test --------
def test_connection():
    if not db.is_closed():
        db.close()
    connection = db.connect()
    assert connection
    if not db.is_closed():
        db.close()


# -------- empty database tests --------


def test_coin_table_is_empty(empty_database):

    coins = Coin.select()
    assert list(coins) == []


def test_add_a_coin(empty_database):
    Coin.insert(coin_name="Automate", coin_path="automate").execute()
    coin = Coin.select().first()
    assert is_valid_uuid(coin.id)
    assert coin.coin_name == "Automate"


def test_add_a_duty(empty_database):
    Duty.insert(duty_number=1, description="Script and code").execute()
    duty = Duty.select().first()
    assert is_valid_uuid(duty.id)
    assert "code" in duty.description
    assert type(duty.duty_number) is int


# -------- full database tests --------


def test_5_coins_exist(full_database):
    assert Coin.select().count() == 5


def test_13_duties_exist(full_database):
    assert Duty.select().count() == 13


def test_assemble_coin_exists(full_database):
    assemble = Coin.select().where(Coin.coin_name == "Assemble")
    assert assemble.exists()


def test_duty_10_is_monitoring(full_database):
    duty_10 = Duty.get(Duty.duty_number == 10)
    assert "monitoring" in duty_10.description


def test_duty_8_is_architecture(full_database):
    duty_8 = Duty.get(Duty.duty_number == 8)
    assert "architecture" in duty_8.description


# ------ test duties can be added to coins ---------------


def test_add_duty_to_coin(full_database):
    assemble = Coin.get(Coin.coin_name == "Assemble")
    assemble_duties = [duty.duty_number for duty in assemble.duties]
    assert len(assemble_duties) == 0

    duty_8 = Duty.get(Duty.duty_number == 8)
    assemble.duties.add(duty_8)

    assemble_duties = [duty.duty_number for duty in assemble.duties]
    assert len(assemble_duties) == 1
    assert 8 in assemble_duties
    assert 7 not in assemble_duties


def test_add_two_duties_to_coin(full_database):
    houston = Coin.get(Coin.coin_name == "Houston, Prepare to Launch")
    houston_duties = [duty.duty_number for duty in houston.duties]
    assert len(houston_duties) == 0

    duty_5 = Duty.get(Duty.duty_number == 5)
    duty_7 = Duty.get(Duty.duty_number == 7)
    duty_10 = Duty.get(Duty.duty_number == 10)
    houston.duties.add([duty_5, duty_7, duty_10])

    houston_duties = {duty.duty_number for duty in houston.duties}
    assert houston_duties == {5, 7, 10}
    assert len(houston_duties) == 3


def test_coin_has_completion_marker(full_database):
    houston = Coin.get(Coin.coin_name == "Houston, Prepare to Launch")
    completion_marker = houston.is_complete
    assert type(completion_marker) == bool


# -------- test no duplication of duties or coins ---------


def test_duty_with_same_number_not_allowed(full_database):
    with pytest.raises(peewee.IntegrityError) as error:
        Duty.insert(duty_number=1, description="Script and code").execute()

    if os.getenv("DB_ENVIRONMENT") in ["rtest", "prod"]:
        db.rollback()

    assert "unique constraint" in str(error.value).lower()


def test_coin_with_same_name_not_allowed(full_database):
    # should insert successfully
    Coin.insert(coin_name="New Coin", coin_path="newcoin").execute()
    with pytest.raises(peewee.IntegrityError) as error:
        # should raise an error
        Coin.insert(coin_name="Automate", coin_path="automate").execute()

    if os.getenv("DB_ENVIRONMENT") in ["rtest", "prod"]:
        db.rollback()

    assert "unique constraint" in str(error.value).lower()
