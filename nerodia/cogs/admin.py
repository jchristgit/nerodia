"""
Administrative commands
for supervising the status
of the bot as well as
controlling it.
"""

import discord
from discord.ext import commands


class Administration:
    """
    A cog for performing administrative
    actions on the bot as well as
    monitoring its status.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="admindashboard", aliases=["adb"])
    @commands.is_owner()
    async def dashboard(self, ctx):
        """Displays a dashboard for the bot administrator.
        This shows an overview about
        the threads, as well as other
        useful information.
        """
        await ctx.trigger_typing()

        await ctx.send(embed=discord.Embed(
            title="Nerodia: Admin Dashboard",
            colour=discord.Colour.blue()
        ))
