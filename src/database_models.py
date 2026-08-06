import os
import uuid

import dotenv
from peewee import *

from src.database import db

dotenv.load_dotenv()

test_schema = 'coins-dev'
prod_schema = 'coins-prod'

if os.getenv('DB_ENVIRONMENT') == 'prod':
    current_schema = prod_schema
elif os.getenv('DB_ENVIRONMENT') in ['ltest', 'rtest'] :
    current_schema = test_schema
else:
    raise ValueError("Please ensure you have a .env file with DB_ENVIRONMENT set to 'ltest', 'rtest' or 'prod'")

class BaseModel(Model):
    class Meta:
        database = db
        if os.getenv('DB_ENVIRONMENT') in ['rtest', 'prod']:
            schema = current_schema

class Duty(BaseModel):
    id = UUIDField(column_name='duty_id', default=uuid.uuid4, primary_key=True)
    description = TextField()
    duty_number = IntegerField(unique=True)
    
    class Meta:
        table_name = 'duties'

class Coin(BaseModel):
    id = UUIDField(column_name='coin_id', default=uuid.uuid4, primary_key=True)
    coin_name = TextField(unique=True)
    coin_path = TextField(unique=True)
    duties = ManyToManyField(Duty, backref='coins')
    is_complete = BooleanField(default=False)
    
    class Meta:
        table_name = 'coins'

class User(BaseModel):
    id = UUIDField(column_name='user_uuid', default=uuid.uuid4, primary_key=True)
    username = TextField(unique=True)
    role = TextField()
    hashed_password = TextField()

    class Meta:
        table_name = 'users'
