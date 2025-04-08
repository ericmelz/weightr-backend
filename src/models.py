from pydantic import BaseModel


class TokenSession(BaseModel):
    """Access Token and Refresh Token for Withings client authentication"""
    access_token: str
    refresh_token: str
