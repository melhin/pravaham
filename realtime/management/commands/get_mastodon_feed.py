import json
import logging
import urllib

import httpx
from django.conf import settings
from django.core.management.base import BaseCommand
from httpx_sse import connect_sse

from posts.publisher import RedisConnectionFactory

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--domain",
            type=str,
            help="Provide the domain that you want to stream",
        )

    def handle(self, *args, **options):
        url = urllib.parse.urljoin(options["domain"], "/api/v1/streaming/public")
        headers = {"Authorization": f"Bearer {settings.MASTODON_BEARER_TOKEN}"}
        logging.info(
            f"Connecting to :{url} and sending messages to {settings.COMMON_STREAM}"
        )

        connection = RedisConnectionFactory().get_connection()
        with httpx.Client() as client:
            with connect_sse(client, "GET", url=url, headers=headers) as event_source:
                for sse in event_source.iter_sse():
                    try:
                        data = json.loads(sse.data)
                    except Exception as ex:
                        logger.error("%s: %s" % (ex, sse.data))
                        logger.error("!" * 10)
                        continue
                    if sse.event == "update":
                        if not data["sensitive"]:
                            dct = {
                                "account": data["account"]["acct"],
                                "content": data["content"],
                                "created_at": data["created_at"],
                                "tags": "".join(ele["name"] for ele in data["tags"]),
                            }
                            logger.info(
                                f"{dct['created_at']} {dct['account']}: {dct['content']} | {dct['tags']}"
                            )
                            logger.info("#" * 10)
                            connection.xadd(
                                name=settings.COMMON_STREAM,
                                fields={"v": json.dumps(dct)},
                            )
