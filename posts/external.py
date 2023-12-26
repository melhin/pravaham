import json
import logging
from uuid import UUID

from django.conf import settings
from redis import ConnectionPool, Redis

from commons.share import Singleton

logger = logging.getLogger(__name__)


class RedisConnectionFactory(metaclass=Singleton):
    """A singleton instance for redis connections for producer"""

    def __init__(self, max_connections=5):
        logger.info("Connecting to redis using a connection pool")
        self.connection_pool = ConnectionPool.from_url(
            url=settings.REDIS_DSN, max_connections=max_connections
        )

    def get_connection(self):
        return Redis(connection_pool=self.connection_pool)


def produce(message: dict, connection_factory=RedisConnectionFactory):
    logger.info("Sending message")
    pubsub = connection_factory().get_connection()
    pubsub.publish(settings.NOTIFICATION_POST, json.dumps(message))


def get_last_messages_from_stream(connection_factory=RedisConnectionFactory):
    connection = connection_factory().get_connection()
    messages = connection.xrevrange(settings.COMMON_STREAM, "+", "-", count=10)
    messages.reverse()
    return messages


def set_last_seen(
    uuid: UUID,
    last_seen: str,
    connection_factory=RedisConnectionFactory,
    expire_in: int = 500,
):
    connection = connection_factory().get_connection()
    connection.set(str(uuid), last_seen, ex=expire_in)


def get_messages_from_stream(
    last_id: str | None = None, connection_factory=RedisConnectionFactory
):
    logger.info("Fetching from stream")
    connection_factory = connection_factory()
    connection = connection_factory.get_connection()
    if not last_id:
        return connection.xrevrange(settings.COMMON_STREAM, "+", "-", count=10)
    return connection.xrevrange(settings.COMMON_STREAM, "+", f"({last_id}")


def get_last_seen(
    uuid: UUID,
    connection_factory=RedisConnectionFactory,
):
    connection = connection_factory().get_connection()
    return connection.get(str(uuid))
