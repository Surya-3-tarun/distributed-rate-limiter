from fastapi import FastAPI, Request, HTTPException
from rate_limiter import is_allowed
from config import FREE_USER_LIMIT, PREMIUM_USER_LIMIT, ANON_IP_LIMIT

app = FastAPI()

def get_user_tier(request: Request):
    # Simulate user authentication via header
    user_id = request.headers.get("X-User-ID")
    user_type = request.headers.get("X-User-Type")  # free / premium

    if user_id and user_type:
        return f"user:{user_id}", user_type
    return None, None


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host

    user_identifier, user_type = get_user_tier(request)

    if user_identifier:
        limit = PREMIUM_USER_LIMIT if user_type == "premium" else FREE_USER_LIMIT
        identifier = user_identifier
    else:
        identifier = f"ip:{client_ip}"
        limit = ANON_IP_LIMIT

    if not is_allowed(identifier, limit):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    response = await call_next(request)
    return response


@app.get("/")
def home():
    return {"message": "API is working"}
