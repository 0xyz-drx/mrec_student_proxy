import os

import httpx
from fastapi import APIRouter, Depends, HTTPException

from app.core.jwt_auth import require_auth

router = APIRouter(prefix="/student", tags=["student"])

IMG_URL = os.getenv("IMG_URL", "")
BASIC_INFO_URL = os.getenv("BASIC_INFO_URL", "")
SEM_RESULTS_URL = os.getenv("OVERALL_MARKS_SHEET", "")


@router.get("/{roll_no}/basic")
async def get_basic_info(
    roll_no: str,
    user=Depends(require_auth),
):
    if user.get("roll_no") != roll_no:
        raise HTTPException(403, "Access denied")

    async with httpx.AsyncClient(verify=False, timeout=10) as client:
        r = await client.get(BASIC_INFO_URL.format(roll_no=roll_no))
        r.raise_for_status()
        return r.json()


@router.get("/{roll_no}/results")
async def get_sem_results(
    roll_no: str,
    user=Depends(require_auth),
):
    if user.get("roll_no") != roll_no:
        raise HTTPException(403, "Access denied")

    async with httpx.AsyncClient(verify=False, timeout=10) as client:
        r = await client.get(SEM_RESULTS_URL.format(roll_no=roll_no))
        r.raise_for_status()
        return r.json()


@router.get("/{roll_no}/photo")
async def get_photo(
    roll_no: str,
    user=Depends(require_auth),
):
    if user.get("roll_no") != roll_no:
        raise HTTPException(403, "Access denied")

    async with httpx.AsyncClient(verify=False, timeout=10) as client:
        r = await client.get(IMG_URL.format(roll_no=roll_no))
        r.raise_for_status()
        return {
            "content_type": r.headers.get("content-type"),
            "image": r.content.hex(),
        }
