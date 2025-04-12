from botocore.client import BaseClient
import boto3
import json
import os
import mysql.connector
from mysql.connector.pooling import PooledMySQLConnection
from dataclasses import dataclass, asdict


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
    conn = mysql.connector.connect(
        host=os.environ.get("DB_HOST"),
        database=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASS")
    )

    with conn.cursor() as cur:
        cur.execute("SELECT VERSION();")
        print(cur.fetchone())

    # all_users = get_all_users(conn)
    #
    # sqs = boto3.client("sqs")
    #
    # for user in all_users:
    #     add_user_data_to_queue(sqs=sqs, user=user, queue_url=os.environ.get("QUEUE_URL"))
