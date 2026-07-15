from src.coins_ui import app
from src.database_models import Coin, Duty
from fastapi.testclient import TestClient
import os, logging


if os.getenv('DB_LOGGING') == 'on':
    logging.getLogger('peewee').addHandler(logging.StreamHandler())
    logging.getLogger('peewee').setLevel(logging.DEBUG)

# ------------ create test client ----------------
client = TestClient(app)

# ----- welcome page -----

def test_welcome_page_returns_message():
    response = client.get("/")
    assert response.status_code == 200
    assert "Please select" in response.text

def test_welcome_page_returns_html_page():
    response = client.get("/")
    assert "<!DOCTYPE html>" in response.text
    
def test_welcome_page_contains_links():
    response = client.get("/")
    assert "/coins" in response.text
    assert "/duties" in response.text
    assert response.text.count("<a") > 1
    assert response.text.count("</a>") > 1
    
    
# ----- list coins page -----

def test_coin_list_page_has_title(full_database):
    response = client.get("/coins")
    assert response.status_code == 200
    assert "<h2>" in response.text
    assert "Coins" in response.text
    
def test_coin_list_page_has_content(full_database):
    response = client.get("/coins")
    assert "<table>" in response.text
    assert "Assemble" in response.text
    assert "Houston, Prepare" in response.text
    assert "<th>Duties</th>" in response.text
    assert "<th>Complete?</th>" in response.text

def test_duties_list_page_has_title(full_database):
    response = client.get("/duties")
    assert response.status_code == 200
    assert "list of all duties" in response.text
    assert "<h2>" in response.text

def test_duty_list_page_has_content(full_database):
    response = client.get("/duties")
    assert "<table>" in response.text
    assert "Duty 3" in response.text
    assert "Script and code" in response.text
    assert "you build it, you run it" in response.text
    assert "<th>Description</th>" in response.text
    assert "Coins" in response.text
    
def test_duty_list_shows_linked_coins(full_database):
    houston = Coin.get(Coin.coin_name == "Houston, Prepare to Launch")  
    duty_5 = Duty.get(Duty.duty_number == 5)
    duty_7 = Duty.get(Duty.duty_number == 7)
    duty_10 = Duty.get(Duty.duty_number == 10)
    houston.duties.add([duty_5, duty_7, duty_10])
        
    response = client.get("/duties")
    assert "Houston, Prepare to Launch" in response.text
    
def test_edit_coin_page_contains_form(full_database):
    response = client.get("edit-coin/deeper")
    assert "<form" in response.text
    assert "name" in response.text
    assert "path" in response.text
    assert "submit" in response.text

def test_update_and_redirect_on_submit(full_database):
    updates = {
        "duties": [5, 7, 10],
        "completed": "true"
    }
    response = client.post("/edit-coin/houston", data=updates, follow_redirects=False)
    
    houston_coin = Coin.get(Coin.coin_path == "houston")
    houston_duties = set([duty.duty_number for duty in houston_coin.duties])
    assert houston_duties == set([5, 7, 10])
    assert houston_coin.is_complete == True
    
    assert response.status_code == 303
    assert response.headers["location"] == "/coins"


def test_create_coin_page_contains_form(full_database):
    response = client.get("/create-coin")
    assert "<form" in response.text
    assert "name" in response.text
    assert "path" in response.text
    assert "submit" in response.text

def test_single_duty_page_dispalys_specified_duty(full_database):
    response = client.get("/duties/6")
    assert "<table" in response.text
    assert "Duty 6" in response.text
    assert "continuous delivery" in response.text
    assert "Duty 1" not in response.text
    assert "Script and code" not in response.text
    assert "<th>Description</th>" in response.text
    assert "Coins" in response.text
    
def test_post_create_coin_and_redirect(full_database):
    coin_data = {
        "coin_path": "fiftypence",
        "coin_name": "50 Pence",
        "duties": [12]
    }
    response = client.post("/create-coin", data=coin_data, follow_redirects=False)
    
    fifty_pence_coin = Coin.get(Coin.coin_path == "fiftypence")
    fifty_pence_duties = set([duty.duty_number for duty in fifty_pence_coin.duties])
    assert set(fifty_pence_duties) == set([12])
    assert fifty_pence_coin.is_complete == False
    
    assert response.status_code == 303
    assert response.headers["location"] == "/coins"
    