import asyncio
import json
import logging
from typing import AsyncGenerator

from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from django.http import HttpRequest, HttpResponseForbidden, StreamingHttpResponse

from realtime.external import get_async_client

logger = logging.getLogger(__name__)


@sync_to_async
def get_user_from_request(request: HttpRequest) -> User | AnonymousUser:
    return request.user


@sync_to_async
def ais_authenticated(user: User) -> bool:
    return user.is_authenticated


async def stream_posts(request: HttpRequest, *args, **kwargs):
    user = await get_user_from_request(request=request)
    if not await ais_authenticated(user=user):
        return HttpResponseForbidden()

    # async def streamed_events(channel_name: str) -> AsyncGenerator[str, None]:
    async def streamed_events() -> AsyncGenerator[str, None]:
        """Listen for events and generate an SSE message for each event"""

        try:
            async with get_async_client().pubsub() as pubsub:
                await pubsub.subscribe(settings.NOTIFICATION_POST)
                while True:
                    msg = await pubsub.get_message(
                        ignore_subscribe_messages=True, timeout=10
                    )
                    if msg:
                        data = json.loads(msg["data"])
                        event = f"data: {data['created_at']}\n\n".encode("utf-8")
                        logging.info(f"Sending :{event}")
                        yield event

        except asyncio.CancelledError:
            # Do any cleanup when the client disconnects
            # Note: this will only be called starting from Django 5.0; until then, there is no cleanup,
            # and you get some spammy 'took too long to shut down and was killed' log messages from Daphne etc.
            raise

    return StreamingHttpResponse(streamed_events(), content_type="text/event-stream")
