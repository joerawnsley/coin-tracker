import json, os
from src.database import db
from src.database_models import Coin, Duty, User

db_environment = os.getenv('DB_ENVIRONMENT')

if not db_environment == 'prod':
    raise Exception('must set db environment to prod before seeding')

with open('seed_data/seed_data.json') as json_data:
    seed_data = json.load(json_data)
    all_coins = seed_data['coins']
    all_duties = seed_data['duties']
    all_users = seed_data['users']
print("connecting to database")
db.connect()
print("clearing data")
db.drop_tables([Coin, Duty, Coin.duties.get_through_model(), User])
print("building coins and duties table")
db.create_tables([Coin, Duty, Coin.duties.get_through_model(), User])
Coin.insert_many(all_coins).execute()
Duty.insert_many(all_duties).execute()
User.insert_many(all_users).execute()

if not db.is_closed():
    db.close()

print("successfully seeded database")