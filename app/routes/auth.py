import os

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.jwt_auth import generate_token

auth_router = APIRouter(prefix="/auth", tags=["auth"])


SIGN_URL = os.getenv("SIGN_URL")

if not SIGN_URL:
    raise ValueError("SIGN_URL environment variable is not set")


class LoginRequest(BaseModel):
    username: str
    password: str


client = httpx.AsyncClient(timeout=5.0, verify=False)


@auth_router.post("/login")
async def login(data: LoginRequest):
    try:
        print(data.username)
        print(data.password)
        resp = await client.post(
            SIGN_URL,  # pyright: ignore[reportArgumentType]
            json={
                "username": data.username,
                "password": data.password,
                "ipAddress": "127.0.0.1",
                "module": "ExamCell",
                "domain": "REMOVED_DOMAIN",
            },
        )

    except httpx.RequestError as e:
        print(e)
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
