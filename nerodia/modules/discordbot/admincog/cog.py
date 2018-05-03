"""
A command group ('cog') used to aid
in administrating nerodia, with commands
that modify the configuration or change
the loaded consumers and more on-the-fly.
"""

import logging

from discord import Colour, Embed
from discord.ext import commands

from nerodia.core import Nerodia
from nerodia.consumers.discordbot import DiscordBotConsumer


log = logging.getLogger(__name__)


class Administration:
    """Administrative commands, bot owner only."""

    def __init__(self, consumer: DiscordBotConsumer, nerodia: Nerodia):
        self.bot = consumer.bot
        self.consumer = consumer
        self.nerodia = nerodia

    def __unload(self):
        log.debug(f"Successfully unloaded {self.__class__.__name__} cog.")

    @commands.command(name="status")
    @commands.is_owner()
    async def status_command(self, ctx):
        """Show an overview about nerodia's status."""

        result = Embed(title="Status", colour=Colour.blue()).add_field(
            name="Loaded Consumers",
            value=", ".join(c.name for c in self.nerodia.consumers),
        ).add_field(
            name="Loaded Modules", value=", ".join(m.name for m in self.nerodia.modules)
        )
        await ctx.send(embed=result)

    @commands.group(name="load")
    @commands.is_owner()
    async def load_group(self, ctx):
        """Load consumers or modules."""

    @load_group.command(name="module")
    @commands.is_owner()
    async def load_module_command(self, ctx, module_path: str):
        """Load the specified module."""

        if module_path in (m.name for m in self.consumer.modules):
            error_info_embed = Embed(
                title=f"Failed to load module `{module_path}`:",
                description=(
                    "Module is already loaded. "
                    "Use `reload` if you want to reload it."
                ),
                colour=Colour.red(),
            )
            return await ctx.send(embed=error_info_embed)

        try:
            await self.nerodia.load_module(module_path)
        except ValueError as e:
            error_info_embed = Embed(
                title=f"Failed to load module `{module_path}`:",
                description=str(e),
                colour=Colour.red(),
            )
            await ctx.send(embed=error_info_embed)
        else:
            success_embed = Embed(
                description=f"Successfully loaded module `{module_path}`.",
                colour=Colour.green(),
            )
            await ctx.send(embed=success_embed)

    @commands.group(name="unload")
    @commands.is_owner()
    async def unload_group(self, ctx):
        """Unload consumers or modules."""

    @unload_group.command(name="module")
    @commands.is_owner()
    async def unload_module_command(self, ctx, module_path: str):
        """Unload the specified module."""

        try:
            await self.nerodia.unload_module(module_path)
        except ValueError as e:
            error_info_embed = Embed(
                title=f"Failed to unload module `{module_path}`:",
                description=str(e),
                colour=Colour.red(),
            )
            await ctx.send(embed=error_info_embed)
        else:
            success_embed = Embed(
                description=f"Successfully unloaded module `{module_path}`.",
                colour=Colour.green(),
            )
            await ctx.send(embed=success_embed)

    @commands.group(name="reload")
    @commands.is_owner()
    async def reload_group(self, ctx):
        """Reload consumers or modules."""

    @reload_group.command(name="module")
    @commands.is_owner()
    async def reload_module_command(self, ctx, module_path: str):
        await ctx.invoke(self.unload_module_command, module_path)
        await ctx.invoke(self.load_module_command, module_path)
