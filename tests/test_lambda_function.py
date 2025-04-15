import sys
from unittest.mock import Mock

import pytest
from loguru import logger

from src.lambda_function import get_all_users, User, add_user_data_to_queue


@pytest.fixture
def mock_db_connection() -> Mock:
    mock_cursor = Mock()
    mock_cursor.fetchall.return_value = [{"id": "1", "refresh_token": "abc"}, {"id": "2", "refresh_token": "def"}]
    mock_connection = Mock()
    mock_connection.cursor.return_value = mock_cursor
    return mock_connection


def test_get_all_users_returns_expected_list_of_users(mock_db_connection):
    all_users = get_all_users(mock_db_connection)

    assert all_users == [User(id="1", refresh_token="abc"), User(id="2", refresh_token="def")]


def test_get_all_users_logs_expected_messages(mock_db_connection, capsys):
    logger.remove()
    logger.add(sys.stdout, level="INFO")

    get_all_users(mock_db_connection)

    logs_output = capsys.readouterr().out

    assert "Retrieving all users from DB" in logs_output and \
        "Results: [{'id': '1', 'refresh_token': 'abc'}, {'id': '2', 'refresh_token': 'def'}]" in logs_output and \
        "Users extracted from DB: [User(id='1', refresh_token='abc'), User(id='2', refresh_token='def')]" in logs_output


def test_add_user_data_to_queue():
    mock_sqs = Mock()
    mock_sqs.send_message.return_value = None

    add_user_data_to_queue(sqs=mock_sqs, user=User(id="1", refresh_token="abc"), queue_url="queue")

    mock_sqs.send_message.assert_called_once_with(
        QueueUrl="queue",
        MessageBody="{\"user_id\": \"1\", \"refresh_token\": \"abc\"}"
    )
