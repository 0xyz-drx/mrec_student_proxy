import io
import os

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.core.jwt_auth import require_auth
from app.core.logging import debug, error, info, warn

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
    error(f"Missing environment variables: {missing}")
    raise RuntimeError(f"Missing environment variables: {missing}")


async def fetch_upstream(url: str):
    debug("Fetching upstream")
    try:
        async with httpx.AsyncClient(verify=False, timeout=10) as client:
            r = await client.get(url)
            r.raise_for_status()
            info("Successful upstream response")
            return r
    except httpx.RequestError as e:
        error(f"University service unreachable | Error: {str(e)}")
        raise HTTPException(503, "University service unreachable")
    except httpx.HTTPStatusError as e:
        warn(f"University service error: {e.response.status_code}")
        raise HTTPException(502, "University service error")


@router.get("/me/info")
async def get_basic_info(request: Request, user=Depends(require_auth)):
    roll_no = user.get("roll_no")
    if not roll_no:
        warn("Invalid token: missing roll_no")
        raise HTTPException(401, "Invalid token")

    info(f"Fetching basic info for roll_no: {roll_no} from ip: {request.client.host}")
    r = await fetch_upstream(BASIC_INFO_URL.format(roll_no=roll_no))
    try:
        return r.json()
    except ValueError:
        error("Invalid JSON in basic info response")
        raise HTTPException(502, "Invalid response from university service")


@router.get("/me/results")
async def get_sem_results(user=Depends(require_auth)):
    roll_no = user.get("roll_no")
    if not roll_no:
        warn("Invalid token: missing roll_no")
        raise HTTPException(401, "Invalid token")

    info(f"Fetching results for roll_no: {roll_no}")
    r = await fetch_upstream(SEM_RESULTS_URL.format(roll_no=roll_no))
    try:
        return r.json()
    except ValueError:
        error("Invalid JSON in results response")
        raise HTTPException(502, "Invalid response from university service")


@router.get("/me/photo")
async def get_photo(user=Depends(require_auth)):
    roll_no = user.get("roll_no")
    if not roll_no:
        warn("Invalid token: missing roll_no")
        raise HTTPException(401, "Invalid token")

    info(f"Fetching photo for roll_no: {roll_no}")
    r = await fetch_upstream(IMG_URL.format(roll_no=roll_no))

    return StreamingResponse(
        io.BytesIO(r.content),
        media_type=r.headers.get("content-type", "image/jpeg"),
    )
