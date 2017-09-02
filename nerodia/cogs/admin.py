"""
Administrative commands
for supervising the status
of the bot as well as
controlling it.
"""

import discord
from discord.ext import commands

from .. import threads


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
        ).add_field(
            name="Thread Status",
            value='\n'.join(
                ("🍏  **Online**: " if t.is_alive() else "🔴 **Offline**: ") + t.name for t in threads.THREADS
            )
        ))

    @commands.command(name="shutdownthreads")
    @commands.is_owner()
    async def shutdown_threads(self, ctx):
        """Shuts down all worker threads.
        Keep in mind that the threads
        cannot be restarted - to accomplish
        this, the whole bot needs to be
        restarted.

        I am not sure why you
        would want to do this.
        """

        alive_threads = sum(1 for t in threads.THREADS if t.is_alive())
        initial = await ctx.send(embed=discord.Embed(
            title=f"Shutting down a total of {alive_threads} alive threads...",
            colour=discord.Color.orange()
        ))
        await ctx.trigger_typing()
        threads.shutdown_all()
        await initial.edit(embed=discord.Embed(
            title="All threads are now offline.",
            colour=discord.Color.green()
        ))
