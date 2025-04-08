import pytest
import redis
from session import SessionManager


@pytest.fixture(scope="module")
def redis_client():
    client = redis.Redis(host="localhost", port=6379, decode_responses=True)
    yield client
    keys = client.keys("*")
    client.delete(*keys)


async def test_redis_roundtrip(redis_client, session_id, sample_token_session):
    manager = SessionManager(redis_client, "", "", "")
    manager.set(session_id, sample_token_session, ttl=300)
    result = manager.get(session_id)
    assert result.access_token == sample_token_session.access_token
