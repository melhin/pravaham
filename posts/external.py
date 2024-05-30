import json
import logging
import re
from dataclasses import asdict
from functools import cache
from uuid import UUID

import redis.asyncio as aredis
from django.conf import settings
from redis import ConnectionPool, Redis

from commons.share import Singleton
from posts.constants import EXPIRY, LISTEN_TIMEOUT, POST_STREAM_PREFIX, USER_STREAM
from posts.data import DataToSend

logger = logging.getLogger(__name__)


class SyncRedisConnectionFactory(metaclass=Singleton):
    """A singleton instance for redis connections for producer"""

    def __init__(self, max_connections=5):
        logger.info("Connecting to redis using a connection pool")
        self.connection_pool = ConnectionPool.from_url(
            url=settings.REDIS_DSN, max_connections=max_connections
        )

    def get_connection(self):
        return Redis(connection_pool=self.connection_pool)


def get_all_emails_from_text(text: str):
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.findall(pattern, text)

def new_post_notification(
    data_to_be_send: DataToSend,
    connection_factory=SyncRedisConnectionFactory,
    expire_in: int = EXPIRY,
):
    connection_factory = connection_factory()
    redis = connection_factory.get_connection()
    pipeline = redis.pipeline()
    user_emails_to_be_notified = get_all_emails_from_text(data_to_be_send.text)
    for user_email in user_emails_to_be_notified:
        user_key = f"{POST_STREAM_PREFIX}{user_email}"
        pipeline.xadd(name=user_key, fields={"v": json.dumps(asdict(data_to_be_send))})
        pipeline.expire(user_key, expire_in)
        logger.info(f"Sent message to {user_key}: {data_to_be_send.text}")
    pipeline.execute()

def get_last_messages_from_stream(connection_factory=SyncRedisConnectionFactory):
    connection = connection_factory().get_connection()
    messages = connection.xrevrange(settings.COMMON_STREAM, "+", "-", count=10)
    messages.reverse()
    return messages


def set_last_seen(
    uuid: UUID,
    last_seen: str,
    connection_factory=SyncRedisConnectionFactory,
    expire_in: int = EXPIRY,
):
    connection = connection_factory().get_connection()
    connection.set(str(uuid), str(last_seen), ex=expire_in)


def get_messages_from_stream(
    last_id: str | None = None, connection_factory=SyncRedisConnectionFactory
):
    logger.info("Fetching from stream")
    connection_factory = connection_factory()
    connection = connection_factory.get_connection()
    if not last_id:
        return connection.xrevrange(settings.COMMON_STREAM, "+", "-", count=10)
    return connection.xrevrange(settings.COMMON_STREAM, "+", f"({last_id}")


def get_last_seen(
    uuid: UUID,
    connection_factory=SyncRedisConnectionFactory,
):
    connection = connection_factory().get_connection()
    return connection.get(str(uuid))


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