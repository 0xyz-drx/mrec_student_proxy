import time

from fastapi import Request

from app.core.logging import error, info, save_log, warn


def get_client_ip(request: Request) -> str:
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    if request.headers.get("x-real-ip"):
        return request.headers["x-real-ip"]
    return request.client.host if request.client else "unknown"


async def request_logger(request: Request, call_next):
    start = time.time()
    ip = get_client_ip(request)
    path = request.url.path
    method = request.method

    try:
        response = await call_next(request)
        duration = round((time.time() - start) * 1000, 2)

        msg = f"{method} {path} {response.status_code} {duration}ms IP={ip}"

        if response.status_code >= 500:
            error(msg)
            save_log(level="ERROR", message=msg, ip=ip, path=path)
        elif response.status_code >= 400:
            warn(msg)
            save_log(level="WARN", message=msg, ip=ip, path=path)
        else:
            info(msg)
            save_log(level="INFO", message=msg, ip=ip, path=path)

        return response

    except Exception as e:
        msg = f"{method} {path} 500 IP={ip} EXCEPTION={str(e)}"
        error(msg)
        save_log(level="CRITICAL", message=msg, ip=ip, path=path)
        raise
