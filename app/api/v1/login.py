# from dotenv import load_dotenv
import os

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.jwt_auth import generate_token

auth_router = APIRouter(prefix="/auth", tags=["auth"])


SIGN_URL = os.getenv("SIGN_URL", "")


class LoginRequest(BaseModel):
    username: str
    password: str


client = httpx.AsyncClient(
    timeout=5.0,
    verify=True,  # FIXED
)


async def login(data: LoginRequest):
    try:
        resp = await client.post(
            SIGN_URL,
            json={
                "username": data.username,
                "password": data.password,
                "ipAddress": "127.0.0.1",
                "module": "ExamCell",
                "domain": "REMOVED_DOMAIN",
            },
        )
    except httpx.RequestError:
        raise HTTPException(503, "Auth service unreachable")

    if resp.status_code != 200:
        raise HTTPException(401, "Invalid credentials")

    payload = resp.json()

    if "username" not in payload or "roles" not in payload:
        raise HTTPException(502, "Malformed auth response")

    token = generate_token(
        {
            "roll_no": payload["username"],
            "role": payload["roles"],
        }
    )

    return {
        "access_token": token,
        "token_type": "Bearer",
        "expires_in": 1800,
    }
