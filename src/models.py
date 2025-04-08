from pydantic import BaseModel


class TokenSession(BaseModel):
    """Access Token and Refresh Token for Withings client authentication"""
    access_token: str
    refresh_token: str


class WeightRecord(BaseModel):
    """Record containing weight measurement"""
    timestamp: int
    weight_lbs: float


class ErrorResponse(BaseModel):
    """HTTP Error Response"""
    error: str
