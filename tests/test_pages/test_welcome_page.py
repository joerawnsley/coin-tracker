from src.app import app
from fastapi.testclient import TestClient
import os, logging

if os.getenv('DB_LOGGING') == 'on':
    logging.getLogger('peewee').addHandler(logging.StreamHandler())
    logging.getLogger('peewee').setLevel(logging.DEBUG)

# ------------ create test client ----------------
client = TestClient(app)

# ----- welcome endpoint -----

def test_welcome_page_returns_message():
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome" in response.text

def test_welcome_page_returns_html_page():
    response = client.get("/")
    assert "<!DOCTYPE html>" in response.text
    
def test_welcome_page_contains_links():
    response = client.get("/")
    assert "<a href='/coins" in response.text
    assert "<a href='/duties" in response.text
    assert response.text.count("</a>") > 1