import uuid
from urllib.parse import urlencode

import httpx
from fastapi import FastAPI, Request
from fastapi import HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic_settings import BaseSettings

app = FastAPI()

SESSIONS = {}

REDIRECT_URI = "http://perfin.ai:9876/withings-callback"
AUTH_URL = "https://account.withings.com/oauth2_user/authorize2"
TOKEN_URL = "https://wbsapi.withings.net/v2/oauth2"

KG_TO_LBS_MULTIPLIER = 2.20462


class Settings(BaseSettings):
    withings_client_id: str
    withings_client_secret: str


settings = Settings()


@app.get("/withings-login")
def withings_login():
    params = {
        "response_type": "code",
        "client_id": settings.withings_client_id,
        "redirect_uri": REDIRECT_URI,
        "scope": "user.info,user.metrics,user.activity",
        "state": "weightrCheck",  # simple CSRF prevention
    }
    return RedirectResponse(f"{AUTH_URL}?{urlencode(params)}")


@app.get("/withings-callback")
async def callback(request: Request):
    code = request.query_params.get("code")
    async with httpx.AsyncClient() as client:
        resp = await client.post(TOKEN_URL, data={
            "action": "requesttoken",
            "grant_type": "authorization_code",
            "client_id": settings.withings_client_id,
            "client_secret": settings.withings_client_secret,
            "code": code,
            "redirect_uri": REDIRECT_URI,
        })
        token_data = resp.json()["body"]
        access_token = token_data["access_token"]

    # Generate a simple session token
    session_id = str(uuid.uuid4())
    SESSIONS[session_id] = access_token

    # Redirect back to Streamlit
    #return RedirectResponse(f"http://localhost:8501?session_id={session_id}")
    # return JSONResponse(content=resp.json())
    return RedirectResponse(f"/weight?session_id={session_id}")


@app.get("/weight")
async def get_weight(session_id: str):
    # access_token = SESSIONS.get(session_id)
    access_token = '871600de2536e68d71bd4d6dd26084566b509a98'
    print(f"access_token={access_token}")
    if not access_token:
        return JSONResponse({"error": "unauthorized"}, status_code=401)

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post("https://wbsapi.withings.net/measure", data={
                "action": "getmeas",
                "meastype": 1,
                "category": 1,
                "access_token": access_token,
            })
            if resp.status_code == 200:
                data = resp.json()
                weights = [
                    (group["date"], meas["value"] * 10 ** meas["unit"] * KG_TO_LBS_MULTIPLIER)
                    for group in data["body"]["measuregrps"]
                    for meas in group["measures"]
                    if meas["type"] == 1
                ]
                return JSONResponse(content=weights)
            else:
                print(f'Raising exception {resp.status_code}')
                raise HTTPException(
                    status_code=502,
                    detail=f"Failed to fetch Withings data.  Status: {resp.status_code}"
                )
        except httpx.RequestError as e:
            print(f'Raising exception:: {e}')
            raise HTTPException(
                status_code=503,
                detail=f"Network error when contacting Withings: {str(e)}"
            )