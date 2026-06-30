import psycopg as pg
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text

load_dotenv()

user = os.getenv("POSTGRES_USER")
pwd = os.getenv("POSTGRES_PASSWORD")
host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
db = os.getenv("POSTGRES_DB_PT")


connect_str = f'postgresql://{user}:{pwd}@{host}:{port}/{db}'


with pg.connect(connect_str) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT version();")
        print(cur.fetchone())