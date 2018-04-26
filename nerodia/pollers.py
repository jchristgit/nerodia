"""
Polls the Bot's Reddit inbox for new messages,
and the followed Twitch streams for updates.
"""

import asyncio
import logging
import traceback
from typing import List

from .base import Consumer
from .clients import twitch
from .consumers.discordbot.database.common import get_all_follows


log = logging.getLogger(__name__)


async def _stream_poller(consumers: List[Consumer]):
    log.info("Started Twitch stream poller.")

    old_data = {}

    while True:
        all_follows = get_all_follows()
        stream_information = await twitch.get_streams(*all_follows)

        for username, stream in stream_information.items():

            if old_data.get(username, stream) != stream:
                is_online = stream is not None
                for consumer in consumers:
                    if is_online:
                        await consumer.stream_online(stream)
                    else:
                        await consumer.stream_offline(stream)

        await asyncio.sleep(10)
        old_data.update(stream_information)


async def stream_poller(consumers: List[Consumer]):
    """Polls followed streams for any updates.

    Args:
        consumers (List[Consumer]):
            A list of set up consumers.
    """

    try:
        await _stream_poller(consumers)
    except asyncio.CancelledError:
        log.info("Twitch stream poller was cancelled.")
    except Exception as e:
        traceback.print_tb(e.__traceback__)
        log.error(f"Uncaught exception: {e}")
