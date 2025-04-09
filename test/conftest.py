import pytest
from models import TokenSession


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
