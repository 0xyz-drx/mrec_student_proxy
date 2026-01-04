import os
from datetime import datetime, timedelta
from typing import Dict

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from .logging import critical, debug, error, info, warn

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGO = "HS256"
JWT_EXP_MINUTES = 30

if not JWT_SECRET:
    critical("JWT_SECRET is not set in environment variables")
    raise RuntimeError("JWT_SECRET is not set")

security = HTTPBearer()


def generate_token(data: Dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=JWT_EXP_MINUTES)
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)
    info(f"Generated JWT for roll_no: {data.get('roll_no')}")
    return token


def decode_token(token: str) -> Dict:
    if not token:
        critical("Token is missing")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is missing",
        )
    try:
        payload = jwt.decode(
            token, JWT_SECRET, algorithms=[JWT_ALGO], options={"require": ["exp"]}
        )
        debug(f"Validated JWT for roll_no: {payload.get('roll_no')}")
        return payload
    except JWTError as e:
        warn(f"Invalid or expired token attempt: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


def require_auth(
    creds: HTTPAuthorizationCredentials = Depends(security),
) -> Dict:
    return decode_token(creds.credentials)
