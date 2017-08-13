"""
Contains the command group
for the Discord Bot.
"""

import datetime
import discord

from discord.ext import commands

from . import util


PM_URL = "https://www.reddit.com/message/compose?to=Botyy&subject=verification"


def create_instructions() -> discord.Embed:
    """
    Creates an Embed containing the disclaimer
    for adding a Reddit account to your Discord account.
    This should be used for adding a field with the token
    which the user should send to the bot via a direct message.

    Returns:
        discord.Embed: An embed with a disclaimer about user data.
    """

    return discord.Embed(
        title="Connect your Reddit Account",
        colour=discord.Colour.blue(),
        timestamp=datetime.datetime.now()
    ).add_field(
        name="Disclaimer",
        value="By connecting your account, you agree that your "
              "**Discord ID is stored unencrypted for an indefinite "
              "time, along with your Reddit name, and this information "
              "may appear in the bot's log messages**. You can "
              "disconnect a connected account at any time.",
        inline=False
    )


class Nerodia:
    """Commands for interacting with the Nerodia Reddit bot."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        print("[DISCORD] Loaded Commands.")

    @commands.command(name="connectreddit")
    async def connect_reddit(self, ctx):
        """
        Connects your Discord account to your Reddit account.
        Please make sure to carefully read through the
        instructions that this command sends upon invocation.
        """

        token = util.random_string()
        instructions = create_instructions()
        instructions.add_field(
            name="Instructions",
            value=f"Send me a [Reddit Message]({PM_URL}) containing"
                  f"`{token}` to verify your account.",
            inline=False
        )
        await ctx.send(embed=instructions)


def setup(bot):
    bot.add_cog(Nerodia(bot))
