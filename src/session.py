from typing import Optional

import httpx
from redis import Redis

from models import TokenSession


class SessionManager:
    """Manages weightr client sessions.  For example, maintain withings access tokens for clients."""
    def __init__(self, redis_client: Redis, token_url: str, client_id: str, client_secret: str):
        self.redis = redis_client
        self.token_url = token_url
        self.client_id = client_id
        self.client_secret = client_secret

    def set(self, session_id: str, session: TokenSession, ttl: int = 365 * 24 * 60 * 60):
        self.redis.setex(session_id, ttl, session.model_dump_json())

    def get(self, session_id: str) -> Optional[TokenSession]:
        data = self.redis.get(session_id)
        if data:
            return TokenSession.model_validate_json(data)
        return None

    async def refresh(self, session_id: str) -> TokenSession:
        session = self.get(session_id)
        if not session:
            raise Exception(f"No session found for session id {session_id}")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data={
                    "action": "requesttoken",
                    "grant_type": "refresh_token",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "refresh_token": session.refresh_token,
                },
            )
            response.raise_for_status()
            data = response.json()["body"]
            new_session = TokenSession(
                access_token=data["access_token"],
                refresh_token=data["refresh_token"],
                user_id=session.user_id
            )
            self.set(session_id, new_session)
            return new_session
