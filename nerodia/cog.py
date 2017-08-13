"""
Contains the command group
for the Discord Bot.
"""

import datetime
import discord
import time

from discord.ext import commands


PM_URL = "https://www.reddit.com/message/compose?to=Botyy&subject=verification"
CR_INSTRUCTIONS = discord.Embed(
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
).add_field(
    name="Instructions",
    value="[Please send me a Reddit PM](PM_URL) containing the **Token**."
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

        await ctx.send(embed=CR_INSTRUCTIONS)


def setup(bot):
    bot.add_cog(Nerodia(bot))
