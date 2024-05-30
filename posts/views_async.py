import asyncio
import json
import logging
import uuid
from typing import AsyncGenerator

from asgiref.sync import sync_to_async
from django.http import HttpRequest, HttpResponseForbidden, StreamingHttpResponse
from django.views.decorators.http import require_http_methods

from accounts.models import User
from posts.constants import CONNECTION_STREAM
from posts.data import EventType
from posts.external_async import listen_on_multiple_streams, send_status_to_stream

logger = logging.getLogger(__name__)


@sync_to_async
def get_user_from_request(request: HttpRequest) -> User:
    return request.user


@sync_to_async
def ais_authenticated(user: User) -> bool:
    return user.is_authenticated


@require_http_methods(["GET"])
async def stream_new_content_notification(request: HttpRequest, *args, **kwargs):
    user = await get_user_from_request(request=request)
    if not await ais_authenticated(user=user):
        return HttpResponseForbidden()

    async def streamed_events(user: User) -> AsyncGenerator[str, None]:
        """Listen for events and generate an SSE message for each event"""
        connection_id = uuid.uuid4()
        events_count = 0
        last_id_returned = None
        await send_status_to_stream(user=user, event_type=EventType.ONLINE)
        logger.info(f"{user.email}: is now connected")
        while True:
            try:
                message = await listen_on_multiple_streams(
                    user_email=user.email,
                    last_id_returned=last_id_returned,
                )
                if message:
                    last_id_returned = message[0][1][0][0]
                    if message[0][0].decode("utf-8") == CONNECTION_STREAM:
                        connection_data = json.loads(message[0][1][0][1][b"v"])
                        dumped_data = f'<div id=message>{connection_data["text"]}</div>'
                        event = "event: status\n"
                    else:
                        dumped_data = json.dumps(
                            {"new_message_id": last_id_returned.decode("utf-8")}
                        )
                        event = "event: new-notification\n"
                    event += f"data: {dumped_data}\n\n"
                    events_count += 1
                    logger.info(f"{connection_id}: Sent events. {events_count}")
                    yield event
                else:
                    event = "event: heartbeat\n"
                    event += "data: ping\n\n"
                    events_count += 1
                    logger.info(f"{connection_id}: Sending heartbeats")
                    yield event

            except asyncio.CancelledError:
                await send_status_to_stream(
                    user=user, event_type=EventType.OFFLINE
                )
                logging.info(
                    f"{connection_id}: Disconnected after events. {events_count}"
                )
                raise

    return StreamingHttpResponse(
        streamed_events(user=user), content_type="text/event-stream"
    )
