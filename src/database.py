from peewee import PostgresqlDatabase, SqliteDatabase
import os, dotenv

dotenv.load_dotenv()

remote_postgres_db = PostgresqlDatabase(
    'joe',
    user='joe',
    port=25060,
    host=os.getenv('DB_HOST'),
    password=os.getenv('DB_PASSWORD')
    )

sqlite_db = SqliteDatabase('local.db')

if os.getenv('DB_ENVIRONMENT') == 'ltest':
    db = sqlite_db   
if os.getenv('DB_ENVIRONMENT') == 'rtest':
    db = remote_postgres_db
if os.getenv('DB_ENVIRONMENT') == 'prod':
    db = remote_postgres_db