import json
import os

import boto3
from botocore.client import BaseClient
import mysql.connector
from mysql.connector.pooling import PooledMySQLConnection
from loguru import logger

from .models import Settings, User


def get_settings() -> Settings:
    db_host = os.environ["DB_HOST"]
    db_name = os.environ["DB_NAME"]
    db_user = os.environ["DB_USER"]
    db_pass = os.environ["DB_PASS"]
    queue_url = os.environ.get("QUEUE_URL")

    settings = Settings(db_host=db_host, db_name=db_name, db_user=db_user, db_pass=db_pass, queue_url=queue_url)

    return settings


def get_all_users(connection: PooledMySQLConnection) -> list[User]:
    cursor = connection.cursor(dictionary=True)

    select_statement = "SELECT * FROM spotify_user;"
    logger.info("Retrieving all users from DB")
    cursor.execute(select_statement)
    results = cursor.fetchall()
    logger.info(f"Results: {results}")
    users = [User(**entry) for entry in results]
    logger.info(f"Users extracted from DB: {users}")

    cursor.close()

    return users


def add_user_data_to_queue(sqs: BaseClient, user: User, queue_url: str):
    message = json.dumps({"user_id": user.id, "refresh_token": user.refresh_token})
    logger.info(f"Sending message to SQS queue: {message}")
    res = sqs.send_message(QueueUrl=queue_url, MessageBody=message)
    logger.info(f"Message sent to SQS queue. Response: {res}")


def lambda_handler(event, context):
    settings = get_settings()

    connection = mysql.connector.connect(
        host=settings.db_host,
        database=settings.db_name,
        user=settings.db_user,
        password=settings.db_pass
    )
    logger.info("Connecting to DB")

    try:
        all_users = get_all_users(connection)

        sqs = boto3.client("sqs")

        for user in all_users:
            add_user_data_to_queue(sqs=sqs, user=user, queue_url=settings.queue_url)
    except Exception as e:
        logger.error(f"Something went wrong - {e}")
    finally:
        connection.close()
