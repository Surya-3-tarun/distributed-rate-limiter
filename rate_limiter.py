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
# import time
# import redis
# from config import REDIS_HOST, REDIS_PORT, RATE_LIMIT, TIME_WINDOW

# r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# def is_allowed(client_id: str):
#     key = f"rate_limit:{client_id}"
#     now = time.time()

#     pipe = r.pipeline()

#     pipe.zremrangebyscore(key, 0, now - TIME_WINDOW)
#     pipe.zcard(key)
#     pipe.zadd(key, {str(now): now})
#     pipe.expire(key, TIME_WINDOW)

#     _, request_count, _, _ = pipe.execute()

#     return request_count < RATE_LIMIT


import time
import redis
from config import REDIS_HOST, REDIS_PORT,FREE_USER_LIMIT,PREMIUM_USER_LIMIT,ANON_IP_LIMIT, TIME_WINDOW

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# Lua script for atomic sliding window rate limiting
lua_script = """
local key = KEYS[1]
local now = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])

-- Remove old requests
redis.call('ZREMRANGEBYSCORE', key, 0, now - window)

-- Count current requests
local current = redis.call('ZCARD', key)

if current < limit then
    -- Add new request timestamp
    redis.call('ZADD', key, now, now)
    redis.call('EXPIRE', key, window)
    return 1
else
    return 0
end
"""

rate_limit_lua = r.register_script(lua_script)

def is_allowed(identifier: str, limit: int):
    key = f"rate_limit:{identifier}"
    now = time.time()

    allowed = rate_limit_lua(
        keys=[key],
        args=[now, TIME_WINDOW, limit]
    )

    return bool(allowed)


