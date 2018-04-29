"""
Polls the Bot's Reddit inbox for new messages,
and the followed Twitch streams for updates.
"""

import asyncio
import logging
import traceback
from typing import List, Set

from .base import Consumer
from .clients import twitch


log = logging.getLogger(__name__)


async def get_all_follows(consumers: List[Consumer]) -> Set[str]:
    result = set()
    for consumer in consumers:
        for follow in await consumer.get_all_follows():
            result.add(follow)
    return result


async def _stream_poller(consumers: List[Consumer]):
    log.info("Started Twitch stream poller.")

    old_data = {}

    while True:
        all_follows = await get_all_follows(consumers)
        stream_information = await twitch.get_streams(*all_follows)

        for username, stream in stream_information.items():

            if old_data.get(username, stream) != stream:
                is_online = stream is not None
                user = await twitch.get_user(username)
                for consumer in consumers:
                    if is_online:
                        await consumer.stream_online(stream, user)
                    else:
                        await consumer.stream_offline(user)

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
        log.error(f"{e.__class__.__name__}: {str(e)}")
