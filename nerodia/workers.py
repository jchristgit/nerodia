"""
Polls the Bot's Reddit inbox for new messages.
"""

import asyncio
import logging

from discord.ext import commands

from .clients import reddit, twitch
from .database.common import get_all_follows
from .handlers import handle_message, handle_stream_update


log = logging.getLogger(__name__)


async def inbox_poller(bot: commands.Bot):
    await bot.wait_until_ready()
    log.info("Started reddit inbox poller.")
    while True:
        for msg in reddit.inbox.unread():
            handle_message(msg)
            msg.mark_read()
        await asyncio.sleep(10)


async def stream_poller(bot: commands.Bot):
    await bot.wait_until_ready()
    log.info("Started Twitch stream poller.")

    old_data = {}
    while True:
        all_follows = get_all_follows()
        stream_information = await twitch.get_streams(*all_follows)
        for username, stream in stream_information.items():
            if old_data.get(username, default=stream) != stream:
                is_online = stream is not None
                log.info(f"Stream status for {username} changed, now {is_online}. Sending an update...")
                await handle_stream_update(bot, username, is_online, stream)

        await asyncio.sleep(10)
        old_data = stream_information
