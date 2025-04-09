from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    withings_client_id: str
    withings_client_secret: str
    redis_host: str
    redis_port: int
