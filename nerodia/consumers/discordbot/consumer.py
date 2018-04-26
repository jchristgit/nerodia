import asyncio
import logging

from .bot import NerodiaDiscordBot
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
        pass

    async def stream_offline(self, stream: Stream):
        pass
