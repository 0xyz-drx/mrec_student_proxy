from fastapi import APIRouter, HTTPException
from app.core.jwt_auth import generate_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(roll_no: str):
    # 🔒 replace this with OTP verification later
    if not roll_no:
        raise HTTPException(status_code=400, detail="Invalid roll number")

    token = generate_token({
        "roll_no": roll_no,
        "role": "student",
    })

    return {
        "access_token": token,
        "token_type": "Bearer",
        "expires_in": 1800,
    }

