import asyncio
import logging
from typing import Iterable

from .bot import NerodiaDiscordBot
from .database import guilds as guild_db
from .database.common import session as db_session
from .database.models import Follow
from .embeds import create_stream_online_embed
from nerodia.base import Consumer, Module
from nerodia.core import Nerodia
from nerodia.config import CONFIG
from nerodia.twitch import TwitchClient, TwitchStream, TwitchUser

log = logging.getLogger(__name__)


class DiscordBotConsumer(Consumer):
    name = "discordbot"

    def __init__(self, twitch_client: TwitchClient, nerodia: Nerodia):
        self.bot = NerodiaDiscordBot(twitch_client)
        self.bot_task = None
        self.nerodia = nerodia
        self.modules = set()

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

    async def load_module(self, module: Module):
        await module.attach(self)
        self.modules.add(module)

    async def unload_module(self, module_name: str):
        module = next((m for m in self.modules if m.name == module_name), None)

        if module is None:
            log.error(
                f"Tried unloading module {module_name} from {self.__class__.__name__}, "
                "but it is currently not loaded."
            )
            raise ValueError(f"Cannot unload unloaded module {module_name}")

        await module.detach(self)
        self.modules.remove(module)
