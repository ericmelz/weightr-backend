from pydantic_settings import BaseSettings
from pydantic import SecretStr


class Settings(BaseSettings):
    withings_client_id: str
    withings_client_secret: SecretStr
    redis_host: str
    redis_port: int
    frontend_url: str
    logging_conf_file: str
    redirect_uri: str
