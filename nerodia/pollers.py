import asyncio
import logging
import traceback
from typing import List, Set

from .base import Consumer
from .twitch import TwitchClient


log = logging.getLogger(__name__)


async def get_all_follows(consumers: List[Consumer]) -> Set[str]:
    """Get all followed streams across all consumers.

    Args:
        consumers (List[Consumer]):
            A list of enabled consumers.

    Returns:
        Set[str]:
            A list of Twitch stream names that are followed,
            retrieved across all enabled consumers.
    """

    return {
        follow for consumer in consumers for follow in await consumer.get_all_follows()
    }


async def _stream_poller(consumers: List[Consumer], twitch_client: TwitchClient):
    """The actual Twitch stream poller.

    Args:
        consumers (List[Consumer]):
            A list of enabled consumers.
        twitch_client (TwitchClient):
            The Twitch client to execute requests with.

    Notes:
        If this coroutine is started directly as a `asyncio.Task`,
        any exceptions thrown within may not propagate properly.
    """

    log.info("Started Twitch stream poller.")

    old_data = {}

    while True:
        all_follows = await get_all_follows(consumers)
        stream_information = await twitch_client.get_streams(*all_follows)

        for username, stream in stream_information.items():

            if old_data.get(username, stream) != stream:
                is_online = stream is not None
                user = await twitch_client.get_user(username)
                for consumer in consumers:
                    if is_online:
                        await consumer.stream_online(stream, user)
                    else:
                        await consumer.stream_offline(user)

        await asyncio.sleep(10)
        old_data.update(stream_information)


async def stream_poller(consumers: List[Consumer], twitch_client: TwitchClient):
    """Starts the stream poller task and catches any exceptions thrown.

    Args:
        consumers (List[Consumer]):
            A list of set up consumers.
        twitch_client (TwitchClient):
            The Twitch client to execute requests with.
    """

    try:
        await _stream_poller(consumers, twitch_client)
    except asyncio.CancelledError:
        log.info("Twitch stream poller was cancelled.")
    except Exception as e:
        traceback.print_tb(e.__traceback__)
        log.error(f"{e.__class__.__name__}: {str(e)}")
