from botocore.client import BaseClient
import boto3
import json
import os
import mysql.connector
from mysql.connector.pooling import PooledMySQLConnection
from dataclasses import dataclass, asdict

DB_HOST = os.environ["DB_HOST"]
DB_NAME = os.environ["DB_NAME"]
DB_USER = os.environ["DB_USER"]
DB_PASS = os.environ["DB_PASS"]
QUEUE_URL = os.environ.get("QUEUE_URL")


@dataclass
class User:
    id: str
    refresh_token: str

    dict = asdict


def get_all_users(conn: PooledMySQLConnection) -> list[User]:
    with conn.cursor() as cur:
        select_statement = "SELECT * FROM spotify_user;"
        cur.execute(select_statement)
        results = cur.fetchall()
        users = [User(**entry) for entry in results]

    return users


def add_user_data_to_queue(sqs: BaseClient, user: User, queue_url: str):
    message = json.dumps(user.dict)
    sqs.send_message(QueueUrl=queue_url, MessageBody=message)


def lambda_handler(event, context):
    connection = mysql.connector.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
    delete_table_statements = [
        "DROP TABLE IF EXISTS top_artist",
        "DROP TABLE IF EXISTS top_track"
    ]

    with connection.cursor() as cursor:
        for delete_statement in delete_table_statements:
            cursor.execute(delete_statement)
            connection.commit()
    # all_users = get_all_users(connection)
    connection.close()

    # sqs = boto3.client("sqs")
    #
    # for user in all_users:
    #     add_user_data_to_queue(sqs=sqs, user=user, queue_url=QUEUE_URL)
