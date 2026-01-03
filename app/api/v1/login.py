# from dotenv import load_dotenv
import os

import httpx
from fastapi import APIRouter
from pydantic import BaseModel

from app.core.jwt_auth import generate_token

auth_router = APIRouter(prefix="/auth", tags=["auth"])


SIGN_URL = os.getenv("SIGN_URL", "")


class LoginRequest(BaseModel):
    username: str
    password: str


@auth_router.post("/login")
async def login(data: LoginRequest) -> dict:
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.post(
            SIGN_URL,
            json={
                "username": data.username,
                "password": data.password,
                "ipAddress": "127.0.0.1",
                "module": "ExamCell",
                "domain": "REMOVED_DOMAIN",
            },
        )
        if response.status_code == 200:
            token = generate_token(
                {
                    "roll_no": response.json()["username"],
                    "role": response.json()["roles"],
                }
            )
            return {
                "token": token,
                "token_type": "Bearer",
                "expires_in": 1800,
            }
        else:
            return {"error": "Login failed", "response": response.json()}
