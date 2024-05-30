import json
import logging
from dataclasses import asdict
from datetime import datetime
from datetime import timezone as dt_timezone
from typing import Dict, List
from uuid import UUID

from django.conf import settings
from django.utils import timezone
from redis import ConnectionPool, Redis

from accounts.models import User
from commons.share import Singleton
from posts.constants import EXPIRY, POST_STREAM_PREFIX
from posts.data import DataToSend
from posts.models import Post

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


def new_post_notification(
    user_emails_to_be_notified: List[str],
    data_to_send: DataToSend,
    connection_factory=SyncRedisConnectionFactory,
    expire_in: int = EXPIRY,
):
    connection_factory = connection_factory()
    redis = connection_factory.get_connection()
    pipeline = redis.pipeline()
    for user_email in user_emails_to_be_notified:
        user_key = f"{POST_STREAM_PREFIX}{user_email}"
        pipeline.xadd(name=user_key, fields={"v": json.dumps(asdict(data_to_send))})
        pipeline.expire(user_key, expire_in)
        logger.info(f"Sent message to {user_key}: {data_to_send.text}")
    pipeline.execute()


def set_last_seen(
    uuid: UUID,
    last_seen: str,
    connection_factory=SyncRedisConnectionFactory,
    expire_in: int = EXPIRY,
):
    connection = connection_factory().get_connection()
    connection.set(str(uuid), str(last_seen), ex=expire_in)


def get_last_seen(
    uuid: UUID,
    connection_factory=SyncRedisConnectionFactory,
):
    connection = connection_factory().get_connection()
    return connection.get(str(uuid))


def epoch_to_iso(epoch):
    """Convert Unix timestamp to ISO formatted string"""
    dt = datetime.fromtimestamp(float(epoch))
    return dt.isoformat() + "Z"


def get_new_posts_for_user(user: User) -> Dict[str, str]:
    last_id = get_last_seen(uuid=user.uuid)
    messages = []
    base_query = Post.objects.select_related("creator").filter(
        tags__contains=[user.email]
    )
    if last_id:
        from_date = epoch_to_iso(last_id)
        logger.info(from_date)
        latest_post = None
        post_query = base_query.filter(created_at__gt=from_date).order_by("-id")
        for post in post_query:
            if not latest_post:
                latest_post = post.created_at
            messages.append(
                {
                    "text": post.text,
                    "creator": post.creator.email,
                    "created_at": post.created_at.isoformat(),
                }
            )
        set_last_seen(
            uuid=user.uuid,
            last_seen=latest_post.astimezone(dt_timezone.utc).timestamp(),
        )
    return messages


def get_last_five_posts_for_user(user: User) -> Dict[str, str]:
    messages = []
    base_query = Post.objects.select_related("creator").filter(
        tags__contains=[user.email]
    )
    post_query = base_query.order_by("-id")[:5]
    latest_post = None
    for post in post_query:
        if not latest_post:
            latest_post = post.created_at
        messages.append(
            {
                "text": post.text,
                "creator": post.creator.email,
                "created_at": post.created_at.isoformat(),
            }
        )
    set_last_seen(
        uuid=user.uuid,
        last_seen=(latest_post if latest_post else timezone.now())
        .astimezone(dt_timezone.utc)
        .timestamp(),
    )
    return messages
