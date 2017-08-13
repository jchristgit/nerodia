"""
Contains the command group
for the Discord Bot.
"""

import discord

from discord.ext import commands


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


def setup(bot):
    bot.add_cog(Nerodia(bot))
