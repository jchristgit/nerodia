import logging

import discord
from discord.ext import commands

from . import cog
from nerodia.config import CONFIG
from nerodia.twitch import TwitchClient


DESCRIPTION = (
    "Hello! I am a Bot made for keeping your Discord servers and "
    "Subreddits updated about Twitch streams going online or offline."
)
log = logging.getLogger(__name__)


class NerodiaDiscordBot(commands.AutoShardedBot):
    """The Discord bot that nerodia runs on."""

    def __init__(self, twitch: TwitchClient):
        """Instantiate the Discord bot and attach the Twitch client to it."""

        super().__init__(
            command_prefix=commands.when_mentioned_or(
                CONFIG["consumers"]["discordbot"]["prefix"]
            ),
            description=DESCRIPTION,
            pm_help=True,
            game=discord.Game(name=CONFIG["consumers"]["discordbot"]["game"]),
        )
        self.twitch = twitch
        cog.setup(self)

    async def on_ready(self):
        total_members = sum(1 for _ in self.get_all_members())
        log.info(f"Discord Bot is ready, seeing {total_members} members.")

    async def close(self):
        await super().close()
        log.info("Logged out Discord Bot.")
