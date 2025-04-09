from fastapi import status
from fastapi.testclient import TestClient

from main import app


def test_withings_login_redirect():
    client = TestClient(app)
    response = client.get("/withings-login", follow_redirects=False)
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert "account.withings.com" in response.headers["location"]
