import pytest
from unittest.mock import AsyncMock
from session import SessionManager


@pytest.mark.asyncio
async def test_set_and_get_session(session_id, sample_token_session):
    redis_client = AsyncMock()
    manager = SessionManager(redis_client, "", "", "")
    await manager.set(session_id, sample_token_session, ttl=60)
    redis_client.setex.assert_called_once()

    redis_client.get.return_value = sample_token_session.model_dump_json()
    result = await manager.get(session_id)
    assert result.access_token == sample_token_session.access_token
