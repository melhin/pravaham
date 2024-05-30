import json
import logging
from dataclasses import asdict

import redis.asyncio as aredis
from django.conf import settings
from django.utils import timezone

from accounts.models import User
from commons.share import Singleton
from posts.constants import (
    CONNECTION_STREAM,
    LISTEN_TIMEOUT,
    POST_STREAM_PREFIX,
)
from posts.data import DataToSend, EventType

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
            CONNECTION_STREAM: last_id_returned,
        },
        block=timeout,
    )


async def send_status_to_stream(
    user: User,
    event_type: EventType,
    connection_factory=AsyncRedisConnectionFactory,
):
    data_to_send = DataToSend(
        event_type=event_type.value,
        text=f"{user.email} is {event_type.value}",
        event_at=timezone.now().isoformat(),
    )
    aredis = await connection_factory().get_connection()
    await aredis.xadd(
        name=CONNECTION_STREAM, fields={"v": json.dumps(asdict(data_to_send))}
    )
    logger.info(f"Sent message to {CONNECTION_STREAM}: {data_to_send.text}")
