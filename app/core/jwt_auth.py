import os
from datetime import datetime, timedelta
from typing import Dict

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGO = "HS256"
JWT_EXP_MINUTES = 30

if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET is not set")

security = HTTPBearer()


def generate_token(data: Dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=JWT_EXP_MINUTES)
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)


def decode_token(token: str) -> Dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


def require_auth(
    creds: HTTPAuthorizationCredentials = Depends(security),
) -> Dict:
    return decode_token(creds.credentials)

