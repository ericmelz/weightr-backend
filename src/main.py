import httpx
import os
import uuid
from urllib.parse import urlencode

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse

app = FastAPI()

SESSIONS = {}

CLIENT_ID = os.getenv("WITHINGS_CLIENT_ID")
CLIENT_SECRET = os.getenv("WITHINGS_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8000/callback"

AUTH_URL = "https://account.withings.com/oauth2_user/authorize2"
TOKEN_URL = "https://wbsapi.withings.net/v2/oauth2"


@app.get("/hello")
def hello():
    return "hello"


@app.get("/withings-callback")
def withings_callback():
    return "withings callback!"


@app.get("/login")
def login():
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": "user.metrics",
        "state": "streamlit",  # simple CSRF prevention
    }
    return RedirectResponse(f"{AUTH_URL}?{urlencode(params)}")


@app.get("/callback")
async def callback(request: Request):
    code = request.query_params.get("code")
    async with httpx.AsyncClient() as client:
        resp = await client.post(TOKEN_URL, data={
            "action": "requesttoken",
            "grant_type": "authorization_code",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "redirect_uri": REDIRECT_URI,
        })
        token_data = resp.json()["body"]
        access_token = token_data["access_token"]

    # Generate a simple session token
    session_id = str(uuid.uuid4())
    SESSIONS[session_id] = access_token

    # Redirect back to Streamlit
    return RedirectResponse(f"http://localhost:8501?session_id={session_id}")


@app.get("/weight")
async def get_weight(session_id: str):
    access_token = SESSIONS.get(session_id)
    if not access_token:
        return JSONResponse({"error": "unauthorized"}, status_code=401)

    async with httpx.AsyncClient() as client:
        resp = await client.post("https://wbsapi.withings.net/measure", data={
            "action": "getmeas",
            "meastype": 1,
            "category": 1,
            "access_token": access_token,
        })
    return resp.json()
