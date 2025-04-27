from pydantic_settings import BaseSettings
from pydantic import SecretStr


class Settings(BaseSettings):
    app_env: str
    withings_client_id: str
    withings_client_secret: SecretStr
    redis_host: str
    redis_port: int
