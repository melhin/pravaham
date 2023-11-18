import asyncio
import json
import logging
from typing import AsyncGenerator
import uuid

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


async def stream_content(request: HttpRequest, *args, **kwargs):
    # user = await get_user_from_request(request=request)
    # if not await ais_authenticated(user=user):
    #    return HttpResponseForbidden()

    async def streamed_events() -> AsyncGenerator[str, None]:
        """Listen for events and generate an SSE message for each event"""
        connection_id = uuid.uuid4()
        events_count =  0

        try:
            connection = get_async_client()
            logging.info(f"{connection_id}: Connecting to stream")
            while True:
                logging.info(f"{connection_id}: waiting for messages stream")
                msg = await connection.xread(
                    count=1, block=5000, streams={settings.COMMON_STREAM: "$"}
                )
                if msg:
                    data = json.loads(msg[0][1][0][1][b"v"])
                    dumped_data = json.dumps(data)
                    event = (
                        f"data: {dumped_data}\n\n"
                    )
                    events_count +=  1
                    logging.info(f"{connection_id}: Sent events. {events_count}")
                    yield event.encode("utf-8")

        except asyncio.CancelledError:
            # Do any cleanup when the clent disconnects
            # Note: this will only be called starting from Django 5.0; until then, there is no cleanup,
            # and you get some spammy 'took too long to shut down and was killed' log messages from Daphne etc.
            logging.info(f"{connection_id}: Disconnected after events. {events_count}")
            raise

    return StreamingHttpResponse(streamed_events(), content_type="text/event-stream")
