"""
Contains the command group
used for the Discord Bot.
"""

import datetime
import logging

import discord
from discord.ext import commands

from .database import guilds as guild_db
from nerodia.clients import twitch

log = logging.getLogger(__name__)


class NerodiaDiscordCog:

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="dashboard", aliases=["database"])
    @commands.guild_only()
    async def guild_dashboard(self, ctx):
        """A dashboard for information about the Guild.

        Shows which streams the guild
        this is invoked on is following.

        Aliased to `database`.
        """

        configured_update_channel = guild_db.get_update_channel(ctx.guild.id)
        if configured_update_channel is None:
            update_channel = "No update channel set."
        else:
            update_channel = self.bot.get_channel(configured_update_channel)
            if update_channel is None:
                guild_db.unset_update_channel(ctx.guild.id)
                update_channel = "No update channel set."
            else:
                update_channel = update_channel.mention

        await ctx.send(
            embed=discord.Embed(colour=discord.Colour.blue()).set_author(
                name=f"Guild Dashboard for {ctx.guild.name}",
                icon_url=ctx.guild.icon_url,
            ).add_field(
                name="Followed Streams",
                value=("• " + "\n• ".join(guild_db.get_follows(ctx.guild.id)))
                or "No follows :(",
            ).add_field(
                name="Stream Update Channel", value=update_channel
            )
        )

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    @commands.guild_only()
    async def follow(self, ctx, *stream_names: str):
        """Follows the given streams on the current Guild.

        You can pass in a list of stream names that should
        be followed, for example:
            `n!gfollow discordapp imaqtpie`

        This command requires you to have the
        manage channels permission.
        """

        await ctx.trigger_typing()

        valid_streams = [
            s for s in stream_names if await twitch.get_user(s) is not None
        ]
        present_follows = guild_db.get_follows(ctx.guild.id)
        unique_streams = set(s for s in valid_streams if s not in present_follows)

        await guild_db.follow(ctx.guild.id, *unique_streams)
        await ctx.send(
            embed=discord.Embed(
                title="Follow command",
                colour=discord.Colour.blue(),
                timestamp=datetime.datetime.now(),
            ).add_field(
                name="Newly followed:", value="• " + "\n• ".join(unique_streams)
            ).add_field(
                name="Failed to follow:",
                value="• "
                + "\n• ".join(s for s in stream_names if s not in unique_streams),
            )
        )

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    @commands.guild_only()
    async def unfollow(self, ctx, *stream_names: str):
        """Unfollows the given list of streams on the current Guild.

        You can pass in either a single stream,
        or multiple streams, simply separated by
        a space, for example:
            `n!gunfollow imaqtpie discordapp`

        This command requires the manage channels permission.
        """

        await ctx.trigger_typing()

        unique_streams = set(stream_names)
        old_follows = guild_db.get_follows(ctx.guild.id)
        unfollowed = [s for s in unique_streams if s in old_follows]
        await guild_db.unfollow(ctx.guild.id, *unique_streams)

        await ctx.send(
            embed=discord.Embed(
                title="Unfollow complete", colour=discord.Colour.blue()
            ).add_field(
                name="Unfollowed Streams", value="• " + "\n •".join(unfollowed)
            ).add_field(
                name="Failed to unfollow",
                value="• "
                + "\n •".join(s for s in unique_streams if s not in unfollowed),
            )
        )

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    @commands.guild_only()
    async def setchannel(self, ctx):
        """Sets the stream update announcement channel.

        This will result in all stream updates for the
        current guild to be posted in the channel
        in which the command was invoked.

        Not setting any channel in which the streams
        updates should be announced will result in
        all follows being removed for the guild.

        This has nothing to do with the
        subreddit-specific follows, configurable
        through `n!sfollow` and `n!sunfollow`.
        """

        await ctx.trigger_typing()
        if guild_db.get_update_channel(ctx.guild.id) is not None:
            guild_db.unset_update_channel(ctx.guild.id)
        guild_db.set_update_channel(ctx.guild.id, ctx.message.channel.id)

        await ctx.send(
            embed=discord.Embed(
                title="Set the stream update announcement channel to this channel.",
                colour=discord.Colour.green(),
            )
        )


def setup(bot: commands.Bot):
    """
    Adds the nerodia command
    group to the discord bot.
    """

    bot.add_cog(NerodiaDiscordCog(bot))
    log.info("Added Discord cog to Discord bot.")
