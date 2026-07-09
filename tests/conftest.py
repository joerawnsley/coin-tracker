import pytest, json, os
from src.database import db
from src.models import Coin, Duty
from dotenv import load_dotenv

load_dotenv()

if os.getenv("REMOTE_SCHEMA") != "test":
    pytest.skip(
        '''
        
        TESTING NOT ALLOWED
        
        Skipping all tests because REMOTE_SCHEMA is not set to 'test'.
        
        ''', 
        allow_module_level=True
    )


# --------------- test fixtures -----------------
@pytest.fixture()
def empty_database():
    db.connect()
    db.create_tables([Coin, Duty, Coin.duties.get_through_model()])
    
    yield
    
    db.drop_tables([Coin, Duty, Coin.duties.get_through_model()])
    if not db.is_closed():
        db.close()

with open('seed_data/seed_data.json') as json_data:
    seed_data = json.load(json_data)
    all_coins = seed_data['coins']
    all_duties = seed_data['duties']
    
@pytest.fixture()
def full_database():
    
    db.connect()
    db.create_tables([Coin, Duty, Coin.duties.get_through_model()])
    Coin.insert_many(all_coins).execute()
    Duty.insert_many(all_duties).execute()
    
    yield
    
    db.drop_tables([Coin, Duty, Coin.duties.get_through_model()])
    
    if not db.is_closed():
        db.close()

@pytest.fixture()
def db_with_duties_but_no_coins():
    
    db.connect()
    db.create_tables([Coin, Duty, Coin.duties.get_through_model()])
    Duty.insert_many(all_duties).execute()
    
    yield
    
    db.drop_tables([Coin, Duty, Coin.duties.get_through_model()])
    
    if not db.is_closed():
        db.close()