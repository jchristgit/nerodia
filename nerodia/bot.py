import discord
from discord.ext import commands

from . import cog
from .config import DISCORD_CFG


DESCRIPTION = (
    "Hello! I am a Bot made for keeping your Discord servers and "
    "Subreddits updated about Twitch streams going online or offline."
)


class NerodiaDiscordBot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or("n!"),
            description=DESCRIPTION,
            pm_help=True,
            game=discord.Game(name=DISCORD_CFG['game'])
        )
        cog.setup(self)

    async def on_ready(self):
        print("[DISCORD] Logged in.")
        print(f"ID: {self.user.id}")
        print(f"Total: {len(self.guilds)} Guilds, {len(self.users)} users.")
        print("Invite Link:\n"
              f"https://discordapp.com/oauth2/authorize?&client_id={self.user.id}&scope=bot")


discord_bot = NerodiaDiscordBot()
