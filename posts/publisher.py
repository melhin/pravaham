import json
import logging

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
