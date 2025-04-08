import psycopg2
from botocore.client import BaseClient
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel
import boto3
import json

from settings import Settings


class User(BaseModel):
    id: str
    refresh_token: str


def get_all_users(conn: psycopg2.extensions.connection) -> list[User]:
    with conn.cursor() as cur:
        select_statement = "SELECT * FROM spotify_user;"
        cur.execute(select_statement)
        results = cur.fetchall()
        users = [User(**entry) for entry in results]

    return users


def add_user_data_to_queue(sqs: BaseClient, user: User, queue_url: str):
    message = json.dumps(user.model_dump())
    sqs.send_message(QueueUrl=queue_url, MessageBody=message)


def lambda_handler(event, context):
    settings = Settings()

    conn = psycopg2.connect(
        host=settings.db_host,
        database=settings.db_name,
        user=settings.db_user,
        password=settings.db_pass,
        cursor_factory=RealDictCursor
    )

    all_users = get_all_users(conn)

    sqs = boto3.client("sqs")

    for user in all_users:
        add_user_data_to_queue(sqs=sqs, user=user, queue_url=settings.queue_url)
