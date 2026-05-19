import redis
from flask import current_app

redis_client = None

def get_redis_client():
    global redis_client
    if redis_client is None:
        redis_url = current_app.config.get('REDIS_URL', 'redis://localhost:6379/0')
        redis_client = redis.StrictRedis.from_url(redis_url, decode_responses=True)
    return redis_client
