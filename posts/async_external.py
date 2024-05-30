import logging
from uuid import UUID

import redis.asyncio as aredis
from django.conf import settings

from commons.share import Singleton
from posts.constants import EXPIRY, LISTEN_TIMEOUT, POST_STREAM_PREFIX, USER_STREAM

logger = logging.getLogger(__name__)
class AsyncRedisConnectionFactory(metaclass=Singleton):
    """A singleton instance for redis connections"""

    def __init__(self, max_connections=5):
        logger.info("Connecting to redis using a connection pool")
        self.connection_pool = aredis.ConnectionPool.from_url(
            url=settings.REDIS_DSN, max_connections=max_connections
        )

    async def get_connection(self):
        return aredis.Redis(connection_pool=self.connection_pool)


async def listen_on_multiple_streams(
    user_email: str,
    last_id_returned: str,
    timeout=LISTEN_TIMEOUT,
    connection_factory=AsyncRedisConnectionFactory,
):

    user_key = f"{POST_STREAM_PREFIX}{user_email}"
    logger.info(f"Fetching from stream: {user_key}")
    aredis = await connection_factory().get_connection()
    if not last_id_returned:
        last_id_returned = "$"
    return await aredis.xread(
        count=1,
        streams={
            user_key: last_id_returned,
            USER_STREAM: last_id_returned,
        },
        block=timeout,
    )


async def aset_last_seen(
    uuid: UUID,
    last_seen: str,
    connection_factory=AsyncRedisConnectionFactory,
    expire_in: int = EXPIRY,
):
    connection = await connection_factory().get_connection()
    await connection.set(str(uuid), str(last_seen), ex=expire_in)
