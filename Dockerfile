FROM python:3.12-alpine

# ---- Environment ----
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1

# ---- Install system deps ----
RUN apk add --no-cache \
    ca-certificates \
    curl

# ---- Install uv (fastest & smallest) ----
RUN pip install --no-cache-dir uv

# ---- Workdir ----
WORKDIR /app

# ---- Copy lockfiles first ----
COPY pyproject.toml uv.lock ./

# ---- Copy ENV URL's ---
COPY .env /app/.env

# ---- Install deps (locked) ----
RUN uv sync --frozen

# ---- Copy app ----
COPY main.py .

# ---- Run ----
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
