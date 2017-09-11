"""
Contains the definition for the
Discord Bot which is used as a
simpler frontend to the Reddit
bot for easier configuration.
"""

import discord
from discord.ext import commands

from . import cogs


DESCRIPTION = (
    "Hello! I am a bot made by Volcyy#2359 to be used as a frontend to the Reddit Bot "
    "/u/Botyy. The Reddit Bot is made to update the sidebar of a subreddit when one "
    "of many streams that a subreddit's moderators can follow goes online or offline.\n\n"
    "Please note that since it is not possible for bots to read any connected "
    "accounts from your Discord profile, it is necesary to manually verify your "
    "reddit identity - this has nothing to do with your connection to Reddit on Discord.\n\n"
    "Nerodia isn't endorsed by Discord, Reddit or Twitch and does not "
    "reflect the views or opinions of Discord, Reddit or Twitch."
)


class NerodiaDiscordBot(commands.AutoShardedBot):
    """
    The base class for the discord Bot.
    This is a bit different from the
    usual discord.py bot since it takes
    the login token in the constructor,
    and in exchange takes no arguments
    in the `run` call.
    """

    def __init__(self, token: str, game: str):
        super().__init__(
            command_prefix=commands.when_mentioned_or("n!"),
            description=DESCRIPTION,
            pm_help=True,
            game=discord.Game(name=game)
        )
        self._token = token

        cogs.setup(self)

    async def on_ready(self):
        """
        Event emitted when the bot has finished logging in.
        """

        print("[DISCORD] Logged in.")
        print(f"ID: {self.user.id}")
        print(f"Total: {len(self.guilds)} Guilds, {len(self.users)} users.")
        print("Invite Link:\n"
              f"https://discordapp.com/oauth2/authorize?&client_id={self.user.id}&scope=bot")

    def run(self):
        """
        Start the bot.
        This call does not exit until the bot
        shuts down either through the client
        or signal from the terminal, e.g. ^C.
        """

        super().run(self._token)
