import os

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

RATE_LIMIT = 10        # requests
TIME_WINDOW = 60       # seconds
