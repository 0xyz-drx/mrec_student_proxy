import io
import os

import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.core.jwt_auth import require_auth

router = APIRouter(prefix="/student", tags=["student"])

IMG_URL = os.getenv("IMG_URL")
BASIC_INFO_URL = os.getenv("BASIC_INFO_URL")
SEM_RESULTS_URL = os.getenv("OVERALL_MARKS_SHEET")

missing = {
    "IMG_URL": IMG_URL,
    "BASIC_INFO_URL": BASIC_INFO_URL,
    "OVERALL_MARKS_SHEET": SEM_RESULTS_URL,
}
missing = [k for k, v in missing.items() if not v]
if missing:
    raise RuntimeError(f"Missing environment variables: {missing}")


async def fetch_upstream(url: str):
    try:
        async with httpx.AsyncClient(verify=False, timeout=10) as client:
            r = await client.get(url)
            r.raise_for_status()
            return r
    except httpx.RequestError:
        raise HTTPException(503, "University service unreachable")
    except httpx.HTTPStatusError:
        raise HTTPException(502, "University service error")


@router.get("/me/info")
async def get_basic_info(user=Depends(require_auth)):
    roll_no = user.get("roll_no")
    if not roll_no:
        raise HTTPException(401, "Invalid token")

    r = await fetch_upstream(BASIC_INFO_URL.format(roll_no=roll_no))
    try:
        return r.json()
    except ValueError:
        raise HTTPException(502, "Invalid response from university service")


@router.get("/me/results")
async def get_sem_results(user=Depends(require_auth)):
    roll_no = user.get("roll_no")
    if not roll_no:
        raise HTTPException(401, "Invalid token")

    r = await fetch_upstream(SEM_RESULTS_URL.format(roll_no=roll_no))
    try:
        return r.json()
    except ValueError:
        raise HTTPException(502, "Invalid response from university service")


@router.get("/me/photo")
async def get_photo(user=Depends(require_auth)):
    roll_no = user.get("roll_no")
    if not roll_no:
        raise HTTPException(401, "Invalid token")

    r = await fetch_upstream(IMG_URL.format(roll_no=roll_no))

    return StreamingResponse(
        io.BytesIO(r.content),
        media_type=r.headers.get("content-type", "image/jpeg"),
    )
