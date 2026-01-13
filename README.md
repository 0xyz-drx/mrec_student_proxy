<a href="https://www.digitalocean.com/?refcode=9098f5d46a71&utm_campaign=Referral_Invite&utm_medium=Referral_Program&utm_source=badge"><img src="https://web-platforms.sfo2.cdn.digitaloceanspaces.com/WWW/Badge%201.svg" alt="DigitalOcean Referral Badge" /></a>

> **Status: Still in Development**
>
> This project is under  development. Security hardening features such as
> application-layer abuse resistance and structured audit logging are planned.

---

## Tech Stack

- **Python 3.12**
- **FastAPI**
- **JWT** (stateless authentication)
- **httpx** (async HTTP client)
- **Docker**
- **DigitalOcean App Platform** (behind Cloudflare edge)

---

## Implemented Features

- [x] JWT-based stateless authentication
- [x] Per-user authorization (subject–resource binding)
- [x] IDOR vulnerability prevention
- [x] Controlled API proxying to a legacy university backend
- [x] Isolation of insecure upstream TLS to a single trusted component
- [x] Timeout enforcement for upstream requests
- [x] Upstream failure isolation
- [x] Containerized deployment using Docker

---

## API Endpoints

- `POST /auth/login`  
- `GET /student/me/basic`  
- `GET /student/me/photo`  
- `GET /student/me/results`

---

## Run Locally (using `uv`)

### Prerequisites
- Python **3.12+**
- `uv`

### Install dependencies

```bash
pip install uv
uv sync --frozen --no-dev
```
### Start the server
```bash
uv run uvicorn app.main:app --port 8080
```
### Run with docker
```bash
docker build -t auth-proxy .
docker run -p 8080:8080 --env-file .env auth-proxy
```
### Planned features
- [ ] OTP based login
- [ ] Application-layer abuse resistance (per-user / per-token rate limiting)
- [ ] Structured audit logging for security visibility
