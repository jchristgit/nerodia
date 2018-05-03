import logging

from .cog import Administration as AdminCog
from nerodia.base import Module
from nerodia.consumers.discordbot import DiscordBotConsumer
from nerodia.core import Nerodia


log = logging.getLogger(__name__)


class AdminCogModule(Module):
    name = "discordbot.admincog"

    def __init__(self, nerodia: Nerodia):
        self.nerodia = nerodia

    async def attach(self, consumer: DiscordBotConsumer):
        cog = AdminCog(consumer, self.nerodia)
        consumer.bot.add_cog(cog)
        log.info(
            f"Attached {self.__class__.__name__} to the "
            f"Discord Bot from the DiscordBotConsumer."
        )

    async def detach(self, consumer: DiscordBotConsumer):
        consumer.bot.remove_cog("Administration")
        log.info(
            f"Detached {self.__class__.__name__} from the "
            f"Discord Bot from the DiscordBotConsumer."
        )
