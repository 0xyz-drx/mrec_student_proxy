import os
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

IMG_URL = os.getenv("IMG_URL")
BASIC_INFO_URL = os.getenv("BASIC_INFO_URL")
SEM_RESULTS_URL = os.getenv("OVERALL_MARKS_SHEET")

app = FastAPI(title="University Proxy API")

# Optional: allow Flutter/web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- BASIC STUDENT INFO ----------
@app.get("/student/{roll_no}/basic")
async def get_basic_info(roll_no: str):
    url = BASIC_INFO_URL.format(roll_no=roll_no)

    try:
        async with httpx.AsyncClient(verify=False, timeout=10) as client:
            r = await client.get(url)
            r.raise_for_status()
            return r.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


# ---------- SEMESTER RESULTS ----------
@app.get("/student/{roll_no}/results")
async def get_sem_results(roll_no: str):
    url = SEM_RESULTS_URL.format(roll_no=roll_no)

    try:
        async with httpx.AsyncClient(verify=False, timeout=10) as client:
            r = await client.get(url)
            r.raise_for_status()
            data = r.json()
            if not isinstance(data, dict):
                raise ValueError("Unexpected semester JSON format")
            return data
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


# ---------- STUDENT PHOTO ----------
@app.get("/student/{roll_no}/photo")
async def get_photo(roll_no: str):
    url = IMG_URL.format(roll_no=roll_no)

    try:
        async with httpx.AsyncClient(verify=False, timeout=10) as client:
            r = await client.get(url)
            r.raise_for_status()
            return {
                "content_type": r.headers.get("content-type"),
                "image": r.content.hex(),  # Flutter can decode
            }
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
