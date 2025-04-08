from unittest.mock import MagicMock

from session import SessionManager


def test_set_and_get_session(session_id, sample_token_session):
    redis_client = MagicMock()
    manager = SessionManager(redis_client, "", "", "")
    manager.set(session_id, sample_token_session, ttl=60)
    redis_client.setex.assert_called_once()

    redis_client.get.return_value = sample_token_session.model_dump_json()
    result = manager.get(session_id)
    assert result.access_token == sample_token_session.access_token
