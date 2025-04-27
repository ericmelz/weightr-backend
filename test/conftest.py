import os

import pytest
import redis
from fastapi.testclient import TestClient
from testcontainers.redis import RedisContainer

from weightr_backend.models import TokenSession


@pytest.fixture
def sample_token_session():
    return TokenSession(access_token="access-token", refresh_token="refresh-token", user_id="user-id")


@pytest.fixture
def session_id():
    return "test-session-id"


class FakeRefreshResponse:
    def raise_for_status(self):
        pass

    def json(self):
        return {
            "body": {
                "access_token": "new-token",
                "refresh_token": "new-refresh"
            }
        }


class FakeAsyncClient:
    def __init__(self, fake_post):
        self.post = fake_post

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.fixture
def monkeypatch_refresh(monkeypatch):
    import httpx

    async def fake_post(*args, **kwargs):
        return FakeRefreshResponse()

    monkeypatch.setattr(httpx, "AsyncClient", lambda: FakeAsyncClient(fake_post))


@pytest.fixture(scope="module")
def redis_container():
    """Start a real Redis container before tests and stop it after."""
    with RedisContainer(port=6379) as redis:
        host = redis.get_container_host_ip()
        port = redis.get_exposed_port(6379)

        # Set environment vars for the app if needed
        os.environ["REDIS_HOST"] = host
        os.environ["REDIS_PORT"] = str(port)
        # # Configure pytest-asyncio globally
        # pytest_plugins = ["pytest_asyncio"]
        yield host, port


@pytest.fixture(scope="module")
def redis_client(redis_container):
    host, port = redis_container
    yield redis.Redis(host=host, port=int(port), decode_responses=True)


@pytest.fixture(scope="module")
def app(redis_client):
    """Override the FastAPI app's Redis connection."""
    from weightr_backend.main import app as fastapi_app, get_redis_client

    def override_get_redis_client():
        return redis_client

    fastapi_app.dependency_overrides[get_redis_client] = override_get_redis_client
    return fastapi_app


@pytest.fixture(scope="module")
def client(app):
    """FastAPI test client."""
    return TestClient(app)
