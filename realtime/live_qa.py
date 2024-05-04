import asyncio
import json
import logging
import uuid
from logging import getLogger
from typing import AsyncGenerator

from django import forms
from django.http import HttpRequest, HttpResponse, StreamingHttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from realtime.external import QA, STREAM_MESSAGE_PREFIX, DataToSend

logger = getLogger(__name__)


class QAForm(forms.Form):
    name = forms.CharField(min_length=3)
    question = forms.CharField(min_length=4)


@require_http_methods(["GET"])
async def start_activity(request: HttpRequest, *args, **kwargs):
    return render(
        request,
        "realtime/live_qa/create.html",
    )


@csrf_exempt
@require_http_methods(["POST"])
async def create_question(request: HttpRequest, *args, **kwargs):
    sender = QA()
    stream_name = f"{STREAM_MESSAGE_PREFIX}common"
    form = QAForm(request.POST or None)
    if form.is_valid():
        await sender.send_question_to_stream(
            stream_name=stream_name,
            message=DataToSend(
                name=form.cleaned_data["name"], question=form.cleaned_data["question"]
            ),
        )
        return HttpResponse(status=200)
    else:
        logger.error(form.errors.as_data())
        return HttpResponse(status=400)


@require_http_methods(["GET"])
async def stream_new_activity(request: HttpRequest, *args, **kwargs):

    async def streamed_events() -> AsyncGenerator[str, None]:
        """Listen for events and generate an SSE message for each event"""
        connection_id = uuid.uuid4()
        events_count = 0
        listener = QA()
        last_id_returned = None
        stream_name = f"{STREAM_MESSAGE_PREFIX}common"

        try:
            while True:
                message = await listener.listen(
                    stream_name=stream_name, last_id_returned=last_id_returned
                )
                if message:
                    last_id_returned = message[0][1][0][0]
                    dumped_data = json.dumps(
                        {"new_message_id": last_id_returned.decode("utf-8")}
                    )
                    event = "event: new-notification\n"
                    event += f"data: {dumped_data}\n\n"
                    events_count += 1
                    logging.info(f"{connection_id}: Sent events. {events_count}")
                    yield event
                else:
                    event = "event: heartbeat\n"
                    event += "data: ping\n\n"
                    events_count += 1
                    logging.info(f"{connection_id}: Sending heartbeats")
                    yield event

        except asyncio.CancelledError:
            logging.info(f"{connection_id}: Disconnected after events. {events_count}")
            raise

    return StreamingHttpResponse(streamed_events(), content_type="text/event-stream")


@require_http_methods(["GET"])
async def get_new_questions(
    request: HttpRequest, last_id_returned: str, *args, **kwargs
):
    stream_name = f"{STREAM_MESSAGE_PREFIX}common"
    messages = QA()
    messages_from_stream = await messages.get_messages_from_stream(
        stream_name=stream_name, last_id_returned=last_id_returned
    )
    messages_from_stream.reverse()
    messages = []
    for ele in messages_from_stream:
        post = json.loads(ele[1][b"v"])
        messages.append(
            {
                "name": post["name"],
                "question": post["question"],
            }
        )
    return render(
        request,
        "realtime/live_qa/new_questions.html",
        context={"messages": messages},
    )


@require_http_methods(["GET"])
async def start(request: HttpRequest, *args, **kwargs):
    return render(
        request,
        "realtime/live_qa/start.html",
    )


@require_http_methods(["GET"])
async def questions(request: HttpRequest, name: str, *args, **kwargs):
    stream_server = reverse("realtime:qa-listen")
    stream_name = f"{STREAM_MESSAGE_PREFIX}common"
    messages = QA()
    messages_from_stream = await messages.get_messages_from_stream(
        stream_name=stream_name, last_id_returned=None
    )
    messages = []
    for ele in messages_from_stream:
        post = json.loads(ele[1][b"v"])
        messages.append(
            {
                "name": post["name"],
                "question": post["question"],
            }
        )
    return render(
        request,
        "realtime/live_qa/questions.html",
        context={
            "stream_url": stream_server,
            "messages": messages,
            "name": name,
        },
    )
