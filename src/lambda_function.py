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


def get_all_users(conn: PooledMySQLConnection) -> list[User]:
    with conn.cursor(dictionary=True) as cur:
        select_statement = "SELECT * FROM spotify_user;"
        cur.execute(select_statement)
        results = cur.fetchall()
        users = [User(**entry) for entry in results]

    return users


def add_user_data_to_queue(sqs: BaseClient, user: User, queue_url: str):
    message = json.dumps(asdict(user))
    sqs.send_message(QueueUrl=queue_url, MessageBody=message)


def lambda_handler(event, context):
    connection = mysql.connector.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)

    try:
        all_users = get_all_users(connection)

        sqs = boto3.client("sqs")

        for user in all_users:
            add_user_data_to_queue(sqs=sqs, user=user, queue_url=QUEUE_URL)
    except Exception as e:
        print(f"Something went wrong - {e}")
    finally:
        connection.close()
