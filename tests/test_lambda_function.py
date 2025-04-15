from unittest.mock import Mock

import pytest

from src.lambda_function import get_all_users, User, add_user_data_to_queue


def test_get_all_users():
    mock_cursor = Mock()
    mock_cursor.fetchall.return_value = [{"id": "1", "refresh_token": "abc"}, {"id": "2", "refresh_token": "def"}]
    mock_db_connection = Mock()
    mock_db_connection.cursor.return_value = mock_cursor

    all_users = get_all_users(mock_db_connection)

    assert all_users == [User(id="1", refresh_token="abc"), User(id="2", refresh_token="def")]


def test_add_user_data_to_queue():
    mock_sqs = Mock()
    mock_sqs.send_message.return_value = None

    add_user_data_to_queue(sqs=mock_sqs, user=User(id="1", refresh_token="abc"), queue_url="queue")

    mock_sqs.send_message.assert_called_once_with(
        QueueUrl="queue",
        MessageBody="{\"user_id\": \"1\", \"refresh_token\": \"abc\"}"
    )
