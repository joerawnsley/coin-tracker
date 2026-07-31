from src.app import app
from fastapi.testclient import TestClient
from src.database import db
from src.utils import is_valid_uuid, coin_to_dict
import pytest, json, peewee
from src.database_models import Coin, Duty
import os, logging, base64

if os.getenv('DB_LOGGING') == 'on':
    logging.getLogger('peewee').addHandler(logging.StreamHandler())
    logging.getLogger('peewee').setLevel(logging.DEBUG)

# ------------ create test client ----------------
client = TestClient(app)

test_user_credentials = "testuser:12345678"
encoded_user_credentials = base64.b64encode(test_user_credentials.encode("utf-8")).decode("utf-8")
test_headers = {"Authorization": f"Basic {encoded_user_credentials}"}

test_admin_credentials = "admin:admin"
encoded_admin_credentials = base64.b64encode(test_admin_credentials.encode("utf-8")).decode("utf-8")
admin_headers = {"Authorization": f"Basic {encoded_admin_credentials}"}

# ----- GET /coins -----

def test_coins_route_returns_a_list(full_database):
    response = client.get("/api/coins")
    data = response.json()
    assert isinstance(data, list)

def test_coins_route_returns_5_coins(full_database):
    response = client.get("/api/coins")
    coin_list = response.json()
    assert len(coin_list) == 5
    
def test_first_coin_has_coin_name_and_id(full_database):
    response = client.get("/api/coins")
    first_coin = response.json()[0]
    assert 'coinName' in first_coin
    assert 'id' in first_coin

def test_all_coins_have_coin_name_and_id(full_database):
    response = client.get("/api/coins")
    coin_list = response.json()
    for coin in coin_list:
        assert 'coinName' in coin
        assert 'id' in coin

def test_data_types_in_coin(full_database):
    response = client.get("/api/coins")
    coin_3 = response.json()[3]
    assert type(coin_3['coinName'] == str)
    assert is_valid_uuid(coin_3['id'])
    assert type(coin_3['duties']) == list
    assert type(coin_3['isComplete']) == bool

def test_list_duties_for_coin(full_database):
    client.put('/api/coins/deeper/add-duties', json=[10, 11, 12], headers=test_headers)
    response = client.get('/api/coins/deeper/list-duties')
    
    assert len(response.json()) == 3
    for number in ["10", "11", "12"]:
        assert number in response.text 
    assert "monitoring" in response.text
    assert "publications" in response.text
    assert "automate any manual tasks" in response.text
    
# -------- POST /coins --------

def test_add_coin_with_no_duties_to_empty_db(empty_database):
    
    assert Coin.select().where(Coin.coin_path == 'deeper').first() is None

    coin_data = {
        "coin_name": "Going Deeper",
        "coin_path": "deeper",
    }
    response = client.post("/api/coins", json=coin_data, headers=admin_headers)
    
    assert response.status_code == 201
    assert Coin.select().where(Coin.coin_path == 'deeper').first() is not None

    
def test_add_coin_with_duties_user(db_with_duties_but_no_coins):
    
    assert Coin.select().where(Coin.coin_path == 'deeper').first() is None

    coin_data = {
        "coin_name": "Going Deeper",
        "coin_path": "deeper",
        "duties": ["11", "12"]
    }
    response = client.post("/api/coins", json=coin_data, headers=test_headers)
    assert response.status_code == 401
    
def test_add_coin_with_duties_admin(db_with_duties_but_no_coins):
    
    assert Coin.select().where(Coin.coin_path == 'deeper').first() is None

    coin_data = {
        "coin_name": "Going Deeper",
        "coin_path": "deeper",
        "duties": ["11", "12"]
    }
    response = client.post("/api/coins", json=coin_data, headers=admin_headers)
    
    assert response.status_code == 201
    assert Coin.select().where(Coin.coin_path == 'deeper').first() is not None
    
    new_coin = Coin.get(Coin.coin_path == "deeper")
    new_coin_duties = [duty.duty_number for duty in new_coin.duties.order_by(Duty.duty_number)]
    assert new_coin_duties[0] == 11
    assert len(new_coin_duties) == 2


def test_coin_detail_page_gets_a_single_coin(full_database):
    
    assemble_coin = Coin.get(Coin.coin_path == 'assemble')
    duty_8 = Duty.get(Duty.duty_number == 8)
    assemble_coin.duties.add(duty_8)
    
    response = client.get("/api/coins/assemble")
    data = response.json()
    
    assert type(data) == dict
    assert data["coinName"] == "Assemble"
    assert data["duties"][0] == 8
    
def test_add_coin_returns_201(db_with_duties_but_no_coins):
    
    coin_data = {
        "coin_name": "Going Deeper",
        "coin_path": "deeper",
        "duties": ["11", "12"]
    }
    response = client.post("/api/coins", json=coin_data, headers=admin_headers)
    assert response.status_code == 201
    
# PUT routes for /coins
def test_add_duty_to_coin(full_database):
    
    automate_coin = Coin.get(Coin.coin_path == 'automate')
    automate_duties = set([duty.duty_number for duty in automate_coin.duties])
    assert automate_coin.duties == set([])
    
    client.put(
        "/api/coins/automate/add-duties", 
        json = [1, 2, 3],
        headers=test_headers
        )
    
    automate_coin = Coin.get(Coin.coin_path == 'automate')
    automate_duties = set([duty.duty_number for duty in automate_coin.duties])
    assert automate_duties == set([1, 2, 3])
    
def test_remove_duties_from_coin(full_database):
    houston = Coin.get(Coin.coin_name == "Houston, Prepare to Launch")
    duty_5 = Duty.get(Duty.duty_number == 5)
    duty_7 = Duty.get(Duty.duty_number == 7)
    duty_10 = Duty.get(Duty.duty_number == 10)
    houston.duties.add([duty_5, duty_7, duty_10])
    houston_duties = set([duty.duty_number for duty in houston.duties])
    assert houston_duties == set([5, 7, 10])
    
    client.put(
        "/api/coins/houston/remove-duties", 
        json = [5, 7],
        headers=test_headers
        )
    
    houston = Coin.get(Coin.coin_name == "Houston, Prepare to Launch")
    houston_duties = set([duty.duty_number for duty in houston.duties])
    assert houston_duties == set([10])
    
def test_mark_coin_complete(full_database):
    security_coin = Coin.get(Coin.coin_path == "security")
    assemble_coin = Coin.get(Coin.coin_path == "assemble")
    assert security_coin.is_complete == False
    assert assemble_coin.is_complete == False
    
    response = client.put("/api/coins/security/mark-complete", headers=test_headers)
    
    security_coin = Coin.get(Coin.coin_path == "security")
    assemble_coin = Coin.get(Coin.coin_path == "assemble")
    assert security_coin.is_complete == True
    assert assemble_coin.is_complete == False
    assert '"isComplete":true' in response.text
    client.cookies.delete("access_token")
    

def test_mark_coin_incomplete(full_database):
    security_coin = Coin.get(Coin.coin_path == "security")
    security_coin.update(is_complete=True).execute()
    security_coin = Coin.get(Coin.coin_path == "security")   
    assemble_coin = Coin.get(Coin.coin_path == "assemble")
    assemble_coin.update(is_complete=True).execute()
    assemble_coin = Coin.get(Coin.coin_path == "assemble") 
    
    assert security_coin.is_complete == True
    assert assemble_coin.is_complete == True
    
    response = client.put("/api/coins/security/mark-incomplete", headers=test_headers)

    security_coin = Coin.get(Coin.coin_path == "security")
    assemble_coin = Coin.get(Coin.coin_path == "assemble")
    assert security_coin.is_complete == False
    assert assemble_coin.is_complete == True
    assert '"isComplete":false' in response.text

# DELETE /coins
def test_delete_coin(full_database):
    coins_in_db = set([coin.coin_name for coin in Coin.select()])
    assert coins_in_db == {'Automate', 'Houston, Prepare to Launch', 'Going Deeper', 'Assemble', 'Call Security'}
    
    response = client.delete("/api/coins/security", headers=test_headers)
    
    coins_in_db = set([coin.coin_name for coin in Coin.select()])
    assert coins_in_db == {'Automate', 'Houston, Prepare to Launch', 'Going Deeper', 'Assemble'}
    assert "deleted" in response.text