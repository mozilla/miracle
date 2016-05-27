import redis

from contextgraph.config import REDIS_URI


def create_cache(cache_url=REDIS_URI, _cache=None):
    if _cache is not None:
        return _cache

    pool = redis.ConnectionPool.from_url(
        cache_url,
        max_connections=20,
        socket_timeout=30.0,
        socket_connect_timeout=60.0,
        socket_keepalive=True,
    )
    return RedisClient(connection_pool=pool)


class RedisClient(redis.StrictRedis):

    def close(self):
        self.connection_pool.disconnect()

    def ping(self):
        try:
            self.execute_command('PING')
        except Exception:
            return False
        return True
