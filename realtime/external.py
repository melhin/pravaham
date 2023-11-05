import logging
from functools import cache

import redis.asyncio as aredis
from django.conf import settings

logger = logging.getLogger(__name__)


@cache
def get_async_client() -> aredis.Redis:
    return aredis.from_url(settings.REDIS_DSN)


