# # Fixed Window
# import redis 
# from config import REDIS_HOST, REDIS_PORT, RATE_LIMIT, TIME_WINDOW

# r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# def is_allowed(client_id: str):
#     key = f"fw:{client_id}"

#     current = r.get(key)

#     if current is None:
#         # first request in window
#         r.set(key, 1, ex=TIME_WINDOW)
#         return True

#     if int(current) < RATE_LIMIT:
#         r.incr(key)
#         return True

#     return False


# sliding_window.py
import time
import redis
from config import REDIS_HOST, REDIS_PORT, RATE_LIMIT, TIME_WINDOW

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def is_allowed(client_id: str):
    key = f"rate_limit:{client_id}"
    now = time.time()

    pipe = r.pipeline()

    pipe.zremrangebyscore(key, 0, now - TIME_WINDOW)
    pipe.zcard(key)
    pipe.zadd(key, {str(now): now})
    pipe.expire(key, TIME_WINDOW)

    _, request_count, _, _ = pipe.execute()

    return request_count < RATE_LIMIT
