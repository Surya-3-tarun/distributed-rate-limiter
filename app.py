from fastapi import FastAPI, Request, HTTPException
from rate_limiter import check_limit
from config import IP_RATE_LIMIT, USER_RATE_LIMIT_FREE, USER_RATE_LIMIT_PREMIUM

app = FastAPI()


def get_user_tier(request: Request):
    # Simulated user tier (later could come from DB/JWT)
    tier = request.headers.get("X-User-Tier", "free")
    return tier


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    tier = get_user_tier(request)

    # IP-level protection
    ip_key = f"rate_limit:ip:{client_ip}"
    if not check_limit(ip_key, IP_RATE_LIMIT):
        raise HTTPException(status_code=429, detail="IP rate limit exceeded")

    # User-level limit
    user_id = request.headers.get("X-User-ID", client_ip)
    user_key = f"rate_limit:user:{user_id}"

    if tier == "premium":
        allowed = check_limit(user_key, USER_RATE_LIMIT_PREMIUM)
    else:
        allowed = check_limit(user_key, USER_RATE_LIMIT_FREE)

    if not allowed:
        raise HTTPException(status_code=429, detail="User rate limit exceeded")

    return await call_next(request)

@app.get("/")
def home():
    return {"message": "Rate limiter service running"}

@app.get("/health")
def health():
    return {"status": "ok"}
