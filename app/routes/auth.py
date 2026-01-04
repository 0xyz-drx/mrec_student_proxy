import os

import httpx
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.core.jwt_auth import generate_token
from app.core.logging import critical, debug, error, info, warn

auth_router = APIRouter(prefix="/auth", tags=["auth"])

SIGN_URL = os.getenv("SIGN_URL")
EXAMCELL_DOMAIN = os.getenv("EXAMCELL_DOMAIN")

if not SIGN_URL:
    critical("SIGN_URL environment variable is not set")
    raise RuntimeError("SIGN_URL environment variable is not set")

if not EXAMCELL_DOMAIN:
    critical("EXAMCELL_DOMAIN environment variable is not set")
    raise RuntimeError("EXAMCELL_DOMAIN environment variable is not set")


class LoginRequest(BaseModel):
    username: str
    password: str


@auth_router.post("/login")
async def login(request: Request, data: LoginRequest):
    client_ip = request.client.host
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()
    elif request.headers.get("x-real-ip"):
        client_ip = request.headers["x-real-ip"]

    info(f"Login attempt for username: {data.username} from IP: {client_ip}")

    try:
        async with httpx.AsyncClient(timeout=5.0, verify=False) as client:
            resp = await client.post(
                SIGN_URL,
                json={
                    "username": data.username,
                    "password": data.password,
                    "ipAddress": client_ip,
                    "module": "ExamCell",
                    "domain": EXAMCELL_DOMAIN,
                },
            )
    except httpx.RequestError as e:
        error(f"Auth service unreachable: {str(e)}")
        raise HTTPException(503, "Auth service unreachable")

    if resp.status_code != 200:
        warn(f"Invalid credentials for username: {data.username} from IP: {client_ip}")
        raise HTTPException(401, "Invalid credentials")

    try:
        payload = resp.json()
    except ValueError:
        error("Invalid JSON response from auth service")
        raise HTTPException(502, "Invalid auth service response")

    if "username" not in payload or "roles" not in payload:
        error("Malformed auth response: missing username or roles")
        raise HTTPException(502, "Malformed auth response")

    token = generate_token(
        {
            "roll_no": payload["username"],
            "role": payload["roles"],
        }
    )

    info(f"Successful login for roll_no: {payload['username']} from IP: {client_ip}")
    return {
        "access_token": token,
        "token_type": "Bearer",
        "expires_in": 1800,
    }
