
#@login_required
import asyncio
import json
from typing import AsyncGenerator

from django.conf import settings
from django.http import HttpRequest, StreamingHttpResponse

from realtime.external import get_async_client


async def stream_posts(request: HttpRequest, *args, **kwargs):
    #async def streamed_events(channel_name: str) -> AsyncGenerator[str, None]:
    async def streamed_events() -> AsyncGenerator[str, None]:
        """Listen for events and generate an SSE message for each event"""

        try:
            async with get_async_client().pubsub() as pubsub:
                await pubsub.subscribe(settings.NOTIFICATION_POST)
                while True:
                    msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=10)
                    if msg:
                        data = json.loads(msg['data'])
                        print(data)
                        event = f"data: {data['created_at']}\n\n".encode("utf-8")
                        print(event)
                        yield event

        except asyncio.CancelledError:
            # Do any cleanup when the client disconnects
            # Note: this will only be called starting from Django 5.0; until then, there is no cleanup,
            # and you get some spammy 'took too long to shut down and was killed' log messages from Daphne etc.
            raise

    return StreamingHttpResponse(streamed_events(), content_type="text/event-stream")
