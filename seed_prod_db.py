import json
import os

from argon2 import PasswordHasher

from src.database import db
from src.database_models import Coin, Duty, User, UserRequest

ph = PasswordHasher()
db_environment = os.getenv("DB_ENVIRONMENT")

assert db_environment == "prod", (
    "must set DB_ENVIRONMENT in .env to prod before seeding"
)
print("reading seed data")
with open("seed_data/seed_data.json") as json_data:
    seed_data = json.load(json_data)
    all_coins = seed_data["coins"]
    all_duties = seed_data["duties"]
    all_users = seed_data["users"]

print("hashing user passwords")
hashed_users = [
    {
        "username": user["username"],
        "role": user["role"],
        "hashed_password": ph.hash(user["plaintext_password"]),
    }
    for user in all_users
]

print("connecting to database")
db.connect()
print("clearing existing data")
db.drop_tables([Coin, Duty, Coin.duties.get_through_model(), User, UserRequest])
print("building coins and duties tables")
db.create_tables([Coin, Duty, Coin.duties.get_through_model(), User, UserRequest])
Coin.insert_many(all_coins).execute()
Duty.insert_many(all_duties).execute()
User.insert_many(hashed_users).execute()

if not db.is_closed():
    db.close()

print("successfully seeded database!")
