import pytest

from weightr_backend.session import SessionManager


@pytest.mark.asyncio
async def test_refresh_with_mocked_http(session_id, sample_token_session, monkeypatch_refresh, redis_client):
    manager = SessionManager(redis_client, "https://example.com", "client-id", "client-secret")
    manager.set(session_id, sample_token_session, ttl=60)
    new_session = await manager.refresh(session_id)
    assert new_session.access_token == "new-token"
    assert new_session.refresh_token == "new-refresh"
