import asyncio
import logging

from .bot import NerodiaDiscordBot
from .database import guilds as guild_db
from .embeds import create_stream_online_embed
from nerodia.base import Consumer, Stream
from nerodia.config import CONFIG

log = logging.getLogger(__name__)


class DiscordBotConsumer(Consumer):

    def __init__(self):
        self.bot = NerodiaDiscordBot()
        self.bot_task = None

    async def initialize(self, loop: asyncio.AbstractEventLoop):
        token = CONFIG["consumers"]["discordbot"]["token"]
        self.bot_task = loop.create_task(self.bot.start(token))
        log.info("Initialized DiscordBot consumer.")

    async def cleanup(self):
        if self.bot_task is not None:
            await self.bot.logout()

    async def stream_online(self, stream: Stream):
        followers = guild_db.get_guilds_following(stream.name)

        for guild_id in followers:
            update_channel_id = guild_db.get_update_channel(guild_id)
            if update_channel_id is None:
                log.warning(
                    f"Guild {guild_id} is following {stream_name!r}",
                    "but has no update channel set.",
                )
            else:
                channel = self.bot.get_channel(update_channel_id)
                if channel is None:
                    log.warning(
                        f"Guild {guild_id} has an update channel set, "
                        "but it could not be found."
                    )
                else:
                    embed = await create_stream_online_embed(stream_name, stream)
                    await channel.send(embed=embed)

    async def stream_offline(self, stream: Stream):
        pass
