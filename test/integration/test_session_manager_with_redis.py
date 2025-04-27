from weightr_backend.session import SessionManager


def test_redis_roundtrip(redis_client, session_id, sample_token_session):
    manager = SessionManager(redis_client, "", "", "")
    manager.set(session_id, sample_token_session, ttl=300)
    result = manager.get(session_id)
    assert result.access_token == sample_token_session.access_token
