from botocore.client import BaseClient
import boto3
import json
import os
import mysql.connector
from mysql.connector.pooling import PooledMySQLConnection
from dataclasses import dataclass


@dataclass
class User:
    id: str
    refresh_token: str


def get_all_users(connection: PooledMySQLConnection) -> list[User]:
    cursor = connection.cursor(dictionary=True)

    select_statement = "SELECT * FROM spotify_user;"
    cursor.execute(select_statement)
    results = cursor.fetchall()
    users = [User(**entry) for entry in results]

    cursor.close()

    return users


def add_user_data_to_queue(sqs: BaseClient, user: User, queue_url: str):
    message = json.dumps({"user_id": user.id, "refresh_token": user.refresh_token})
    res = sqs.send_message(QueueUrl=queue_url, MessageBody=message)
    print(f"{res = }")


def lambda_handler(event, context):
    db_host = os.environ["DB_HOST"]
    db_name = os.environ["DB_NAME"]
    db_user = os.environ["DB_USER"]
    db_pass = os.environ["DB_PASS"]
    queue_url = os.environ.get("QUEUE_URL")

    connection = mysql.connector.connect(host=db_host, database=db_name, user=db_user, password=db_pass)

    try:
        all_users = get_all_users(connection)
        print(f"{all_users = }")

        sqs = boto3.client("sqs")

        for user in all_users:
            print(f"{user = }")
            add_user_data_to_queue(sqs=sqs, user=user, queue_url=queue_url)
    except Exception as e:
        print(f"Something went wrong - {e}")
    finally:
        connection.close()
