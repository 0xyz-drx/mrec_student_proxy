from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.logging import critical, info
from app.middleware.request_logger import request_logger
from app.routes.auth import auth_router
from app.routes.student import router as student_router

load_dotenv()

app = FastAPI(title="University Proxy API")
app.middleware("http")(request_logger)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Tighten in production
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(student_router)


@app.on_event("startup")
async def startup_event():
    info("University Proxy API starting up...")
    info("Routes loaded: /auth/login, /student/me/*")


@app.on_event("shutdown")
async def shutdown_event():
    info("University Proxy API shutting down...")
