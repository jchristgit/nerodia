import asyncio
import logging
from typing import Iterable

from .bot import NerodiaDiscordBot
from .database import guilds as guild_db
from .database.common import session as db_session
from .database.models import Follow
from .embeds import create_stream_online_embed
from nerodia.base import Consumer
from nerodia.config import CONFIG
from nerodia.twitch import TwitchStream, TwitchUser

log = logging.getLogger(__name__)


class DiscordBotConsumer(Consumer):

    def __init__(self):
        self.bot = NerodiaDiscordBot()
        self.bot_task = None

    async def initialize(self, loop: asyncio.AbstractEventLoop):
        token = CONFIG["consumers"]["discordbot"]["token"]
        self.bot_task = loop.create_task(self.bot.start(token))
        log.info("Started Discord Bot in background.")

    async def cleanup(self):
        if self.bot_task is not None:
            await self.bot.logout()

    async def stream_online(self, stream: TwitchStream, user: TwitchUser):
        followers = guild_db.get_guilds_following(user.name)

        for guild_id in followers:
            update_channel_id = guild_db.get_update_channel(guild_id)
            if update_channel_id is None:
                log.warning(
                    f"Guild {guild_id} is following {user.name!r}"
                    "but has no update channel set."
                )
            else:
                channel = self.bot.get_channel(update_channel_id)
                if channel is None:
                    log.warning(
                        f"Guild {guild_id} has an update channel set, "
                        "but it could not be found."
                    )
                else:
                    embed = create_stream_online_embed(stream, user)
                    await channel.send(embed=embed)

    async def stream_offline(self, user: TwitchUser):
        pass

    async def get_all_follows(self) -> Iterable[str]:
        return (f.follows for f in db_session.query(Follow))
