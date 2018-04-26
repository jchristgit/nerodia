import logging

import discord
from discord.ext import commands

from . import cog
from nerodia.config import DISCORD_CFG
from nerodia.workers import inbox_poller, stream_poller


DESCRIPTION = (
    "Hello! I am a Bot made for keeping your Discord servers and "
    "Subreddits updated about Twitch streams going online or offline."
)
log = logging.getLogger(__name__)


class NerodiaDiscordBot(commands.AutoShardedBot):
    """The Discord bot that nerodia runs on.

    This is a custom subclass of `commands.AutoShardedBot`
    that is not any different, except that it starts the
    tasks that nerodia uses to update stream statuses and more.

    Attributes:
        inbox_poller (asyncio.Task):
            The background task polling the reddit inbox.
        stream_poller (asyncio.Task):
            The background task polling Twitch stream statuses.
    """

    def __init__(self):
        """Instantiate the Discord bot.

        This sets up the `asyncio.Task`s for background
        updating, and attaches command groups to the bot.
        """

        super().__init__(
            command_prefix=commands.when_mentioned_or("n!"),
            description=DESCRIPTION,
            pm_help=True,
            game=discord.Game(name=DISCORD_CFG["game"]),
        )
        cog.setup(self)
        self.inbox_poller = self.loop.create_task(inbox_poller(self))
        self.stream_poller = self.loop.create_task(stream_poller(self))
        log.info("Started all tasks.")

    async def on_ready(self):
        total_members = sum(1 for _ in self.get_all_members())
        log.info(f"Discord Bot is ready, seeing {total_members} members.")

    async def close(self):
        await super().close()
        log.info("Logged out Discord Bot.")

        self.inbox_poller.cancel()
        self.stream_poller.cancel()
