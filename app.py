from fastapi import FastAPI, Request, HTTPException
from rate_limiter import is_allowed

app = FastAPI()

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host

    if not is_allowed(client_ip):
        raise HTTPException(status_code=429, detail="Too Many Requests")

    response = await call_next(request)
    return response


@app.get("/")
def home():
    return {"message": "API is working"}

@app.get("/health")
def health():
    return {"status": "ok"}
