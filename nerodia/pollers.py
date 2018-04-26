"""
Polls the Bot's Reddit inbox for new messages,
and the followed Twitch streams for updates.
"""

import asyncio
import logging
import traceback

from discord.ext import commands

from .clients import twitch
from .database.common import get_all_follows
from .handlers import handle_stream_update


log = logging.getLogger(__name__)


async def _stream_poller(bot: commands.Bot):
    await bot.wait_until_ready()
    log.info("Started Twitch stream poller.")

    old_data = {}

    while True:
        all_follows = get_all_follows()
        stream_information = await twitch.get_streams(*all_follows)

        for username, stream in stream_information.items():

            if old_data.get(username, stream) != stream:
                is_online = stream is not None
                await handle_stream_update(bot, username, is_online, stream)

        await asyncio.sleep(10)
        old_data.update(stream_information)


async def stream_poller(bot: commands.Bot):
    """Polls followed streams for any updates.

    Args:
        bot (commands.Bot):
            The main bot instance.
    """

    try:
        await _stream_poller(bot)
    except asyncio.CancelledError:
        log.info("Twitch stream poller was cancelled.")
    except Exception as e:
        traceback.print_tb(e.__traceback__)
        log.error(f"Uncaught exception: {e}")
