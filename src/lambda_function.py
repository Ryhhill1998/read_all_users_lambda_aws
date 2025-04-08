import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel

from settings import Settings

settings = Settings()

conn = psycopg2.connect(
    host=settings.db_host,
    database=settings.db_name,
    user=settings.db_user,
    password=settings.db_pass,
    cursor_factory=RealDictCursor
)


class User(BaseModel):
    id: str
    refresh_token: str


def get_all_users(conn: psycopg2.extensions.connection):
    with conn.cursor() as cur:
        select_statement = "SELECT * FROM spotify_user;"
        cur.execute(select_statement)
        results = cur.fetchall()
        users = [User(**entry) for entry in results]
        print(users)


get_all_users(conn)


def add_user_data_to_queue():
    pass


def lambda_handler(event, context):
    pass
