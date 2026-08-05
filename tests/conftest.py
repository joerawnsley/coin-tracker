import pytest, json, os, dotenv
from src.database import db
from src.database_models import Coin, Duty, User

dotenv.load_dotenv()
    
if os.getenv("DB_ENVIRONMENT") == "prod":
    pytest.skip(
        '''
        
        TESTING NOT ALLOWED
        
        DB_ENVIRONMENT in .env must be set to 'ltest' or 'rtest' before running tests 
        
        ''', 
        allow_module_level=True
    )

# --------------- seed data -----------------

with open('seed_data/seed_data.json') as json_data:
    seed_data = json.load(json_data)
    all_coins = seed_data['coins']
    all_duties = seed_data['duties']
    all_users = seed_data['users']

# --------------- test fixtures -----------------
@pytest.fixture()
def empty_database():
    # contains only users but no coins or duties
    db.connect()
    db.create_tables([Coin, Duty, Coin.duties.get_through_model(), User])
    User.insert_many(all_users).execute()

    yield
    
    db.drop_tables([Coin, Duty, Coin.duties.get_through_model(), User])
    if not db.is_closed():
        db.close()


    
@pytest.fixture()
def full_database():
    
    db.connect()
    db.create_tables([Coin, Duty, Coin.duties.get_through_model(), User])
    Coin.insert_many(all_coins).execute()
    Duty.insert_many(all_duties).execute()
    User.insert_many(all_users).execute()
    
    yield
    
    db.drop_tables([Coin, Duty, Coin.duties.get_through_model(), User])
    
    if not db.is_closed():
        db.close()

@pytest.fixture()
def db_with_duties_but_no_coins():
    
    db.connect()
    db.create_tables([Coin, Duty, Coin.duties.get_through_model(), User])
    Duty.insert_many(all_duties).execute()
    User.insert_many(all_users).execute()
    
    yield
    
    db.drop_tables([Coin, Duty, Coin.duties.get_through_model(), User])
    
    if not db.is_closed():
        db.close()