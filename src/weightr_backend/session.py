import logging.config
import os
from pathlib import Path
from typing import Optional

import httpx
import yaml
from redis import Redis

from weightr_backend.conf import Settings
from weightr_backend.models import TokenSession

# TODO NOT SURE IF I NEED TO LOAD SETTINGS AND CONFIG LOGGING HERE
env_file = os.getenv("WEIGHTR_BACKEND_CONF_FILE", "var/conf/weightr-backend/.env")
settings = Settings(_env_file=env_file, _env_file_encoding="utf-8")
config_path = Path(__file__).resolve().parent.parent.parent / "conf" / "logging" / f"{settings.app_env}.yaml"
with open(config_path, "r") as f:
    config = yaml.safe_load(f)
    logging.config.dictConfig(config)

logger = logging.getLogger("app")


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
            logger.debug(f'{session_id=}')
            logger.debug(f'{session=}')
            logger.debug(f'{data=}')
            # TODO access_token can be nonexistent here.  (data={}).  Handle that case.
            new_session = TokenSession(
                access_token=data["access_token"],
                refresh_token=data["refresh_token"],
                user_id=session.user_id
            )
            self.set(session_id, new_session)
            return new_session
