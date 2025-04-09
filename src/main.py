import logging.config
import os
import uuid
from typing import List
from urllib.parse import urlencode

import httpx
import yaml
from fastapi import FastAPI, Request, Depends
from fastapi import HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from redis import Redis

from conf import Settings
from models import WeightRecord, ErrorResponse, TokenSession
from session import SessionManager

settings = Settings()
with open(f"../conf/logging/{settings.app_env}.yaml", "r") as f:
    config = yaml.safe_load(f)
    logging.config.dictConfig(config)

logger = logging.getLogger("app")

logger.info("Starting weightr-backend...")

app = FastAPI(
    title="Weightr Backend",
    description="API backend for the Weightr weight-loss app, integrating Withings for biometric data.",
    version="1.0.0",
    contact={
        "name": "Eric Melz",
        "url": "https://perfin.ai",
        "email": "eric@perfin.ai"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
)

SESSIONS = {}

REDIRECT_URI = "http://perfin.ai:9876/withings-callback"
AUTH_URL = "https://account.withings.com/oauth2_user/authorize2"
TOKEN_URL = "https://wbsapi.withings.net/v2/oauth2"

KG_TO_LBS_MULTIPLIER = 2.20462


async def get_redis_client() -> Redis:
    return Redis(host=settings.redis_host, port=settings.redis_port, decode_responses=True)


def get_session_manager(redis: Redis = Depends(get_redis_client)) -> SessionManager:
    return SessionManager(redis, TOKEN_URL, settings.withings_client_id, settings.withings_client_secret)


@app.get(
    "/withings-login",
    summary="Start Withings OAuth2 login flow",
    description="Redirects the user to Withings for OAuth2 login and authorization.",
    tags=["Auth"],
    responses={
        307: {"description": "Temporary redirect to Withings login page"}
    }
)
def withings_login():
    """Redirect user to Withings login."""
    logger.debug("Initiating withings-login")
    params = {
        "response_type": "code",
        "client_id": settings.withings_client_id,
        "redirect_uri": REDIRECT_URI,
        "scope": "user.info,user.metrics,user.activity",
        "state": "weightrCheck",  # simple CSRF prevention
    }
    url = f"{AUTH_URL}?{urlencode(params)}"
    logger.debug(f"Redirecting to Withings Auth URL: {url}")
    return RedirectResponse(url)


@app.get(
    "/withings-callback",
    summary="Handle OAuth2 callback from Withings",
    description="Exchanges the code from Withings for access/refresh tokens and creates a session ID.",
    tags=["Auth"],
    responses={
        307: {"description": "Redirect to frontend with session_id"},
        502: {"model": ErrorResponse, "description": "Failed to exchange code for tokens"},
        500: {"model": ErrorResponse, "description": "Unexpected internal error"}
    }
)
async def callback(request: Request, session_manager: SessionManager = Depends(get_session_manager)):
    """OAuth2 callback handler for Withings"""
    code = request.query_params.get("code")
    logger.debug(f"withings-callback received auth code {code}")
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(TOKEN_URL, data={
                "action": "requesttoken",
                "grant_type": "authorization_code",
                "client_id": settings.withings_client_id,
                "client_secret": settings.withings_client_secret,
                "code": code,
                "redirect_uri": REDIRECT_URI,
            })
            resp.raise_for_status()
            token_data = resp.json()["body"]
            access_token = token_data["access_token"]
            refresh_token = token_data["refresh_token"]
            logger.debug("Successfully retrieved tokens.")
            logger.debug(f"{access_token=}")
            logger.debug(f"{refresh_token=}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to exchange code: {e.response.status_code} - {e.response.text}")
            raise HTTPException(status_code=502, detail="Failed to exchange authorization code for access tokens")
        except Exception as e:
            logger.exception("Unexpected error during callback.")
            logger.exception(e)
            raise HTTPException(status_code=500, detail="Unexpected error.")

    session = TokenSession(access_token=access_token, refresh_token=refresh_token)
    session_id = str(uuid.uuid4())
    session_manager.set(session_id, session)
    logger.debug(f"Session created: {session_id}")

    # Redirect back to Streamlit
    # TODO: this url should be configurable based on app_env
    return RedirectResponse(f"http://localhost:8501?session_id={session_id}")


@app.get(
    "/weight",
    response_model=List[WeightRecord],
    summary="Get weight data from Withings",
    description="Fetches weight data for the user associated with the given session ID.",
    tags=["Measurements"],
    responses={
        200: {"description": "List of weight records"},
        401: {"model": ErrorResponse, "description": "Invalid or expired session"},
        502: {"model": ErrorResponse, "description": "Upstream Withings API error"},
        503: {"model": ErrorResponse, "description": "Network error"}
    }
)
async def get_weight(session_id: str, session_manager: SessionManager = Depends((get_session_manager))):
    """Fetch weight measurements using the stored Withings token."""
    logger.debug(f"Fetching weight for session {session_id}")
    session = session_manager.get(session_id)

    if not session:
        logger.warning(f"Unauthorized access attempt for session {session_id}")
        return JSONResponse({"error": "unauthorized"}, status_code=401)

    async with httpx.AsyncClient() as client:
        try:
            for attempt in ("original", "refreshed"):
                access_token = session.access_token
                resp = await client.post("https://wbsapi.withings.net/measure", data={
                    "action": "getmeas",
                    "meastype": 1,
                    "category": 1,
                    "access_token": access_token,
                })
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("status") == 0:
                        break
                    elif data.get("status") == 401 and attempt == "original":
                        logger.warning(f"Session {session_id} received 401 with access token={session.access_token}, "
                                       f"indicating access token expired.  Refreshing access token...")
                        session = await session_manager.refresh(session_id)
                        logger.warning(f"Session {session_id} refreshed.  New access token={session.access_token}")
                    else:
                        logger.error(f"Withings measurement api returned error status: {data.get('status')}")
                        logger.exception(f"Unexpected status from withings weight api: {data}")
                        raise HTTPException(status_code=502, detail="Internal server error while fetching weight")
                else:
                    logger.error(f'Unexpected status code from withings: {resp.status_code}')
                    raise HTTPException(
                        status_code=502,
                        detail=f"Failed to fetch Withings data.  Status: {resp.status_code}"
                    )
            weights = [
                WeightRecord(
                    timestamp=group["date"],
                    weight_lbs=meas["value"] * 10 ** meas["unit"] * KG_TO_LBS_MULTIPLIER
                )
                for group in data["body"]["measuregrps"]
                for meas in group["measures"]
                if meas["type"] == 1
            ]
            logger.debug(f"Fetched {len(weights)} weight records.")
            return weights
        except httpx.RequestError as e:
            logger.exception(f"Network error while contacting withings weight api")
            logger.exception(e)
            raise HTTPException(
                status_code=503,
                detail=f"Network error when contacting Withings: {str(e)}"
            )
