import logging
from functools import cache

import redis.asyncio as aredis
from django.conf import settings

from commons.share import Singleton

logger = logging.getLogger(__name__)


@cache
def get_async_client() -> aredis.Redis:
    return aredis.from_url(settings.REDIS_DSN)


class AsyncRedisConnectionFactory(metaclass=Singleton):
    """A singleton instance for redis connections"""

    def __init__(self, max_connections=5):
        logger.info("Connecting to redis using a connection pool")
        self.connection_pool = aredis.ConnectionPool.from_url(
            url=settings.REDIS_DSN, max_connections=max_connections
        )

    async def get_connection(self):
        return aredis.Redis(connection_pool=self.connection_pool)

async def get_messages_from_stream(last_id: str, connection_factory=AsyncRedisConnectionFactory):
    logger.info("Fetching from stream")
    connection_factory = connection_factory()
    connection = await connection_factory.get_connection()
    return await connection.xrange(settings.COMMON_STREAM, "-", f"({last_id}")