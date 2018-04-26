"""
Contains the command group
used for the Discord Bot.
"""

import asyncio
import datetime
import logging
import secrets
from typing import Optional

import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

from . import util
from .clients import reddit, twitch
from .checks import dm_only
from .constants import (
    # Error Embeds
    ALREADY_CONNECTED_EMBED,
    BOT_NOT_MODERATOR_EMBED,
    DM_ONLY_EMBED,
    NO_CONNECTION_EMBED,
    NO_PM_IN_TIME_EMBED,
    UNKNOWN_SUBREDDIT_EMBED,
    USER_NOT_MODERATOR_EMBED,
    # Verification timer settings
    VERIFY_TIMEOUT,
    # Reddit constants
    BOT_REDDIT_NAME,
    PM_URL,
)
from .database import guilds as guild_db, subreddits as sub_db
from .database.models import DRConnection, session as db_session


log = logging.getLogger(__name__)


def create_instructions(token: str) -> discord.Embed:
    """
    Creates an Embed containing the disclaimer
    for attaching a Reddit account to your Discord account.

    Args:
        token (str):
            The token that should be appended to the reddit PM link.

    Returns:
        discord.Embed:
            An embed with a disclaimer about user data, as well as other information
            necessary to link the author's Discord account with their reddit account.
    """

    return discord.Embed(
        title="Connect your Reddit Account",
        colour=discord.Colour.blue(),
        timestamp=datetime.datetime.now(),
        description="You can disconnect your account at any time.",
    ).add_field(
        name="Warning", value="**Do not share this link!**"
    ).add_field(
        name="Instructions",
        value=f"Send me a [Reddit Message]({PM_URL + token}) by clicking on "
        f"the link and clicking `send` to connect your reddit account.",
    ).set_footer(
        text="⏲ You have five minutes of time before the token expires."
    )


async def wait_for_add(user_id: str) -> Optional[str]:
    """
    Waits for the given user to add his reddit
    account.

    Args:
        user_id (str):
            The Discord user ID for the user
            who wants to add his reddit account.

    Returns:
        Optional[str]:
            The reddit name of the user if successful,
            or `None` if no valid direct message containing
            the token was received in time.
    """

    timeout_ctr = VERIFY_TIMEOUT * 60
    while timeout_ctr > 0:
        await asyncio.sleep(5)
        timeout_ctr -= 5
        user = util.verify_dict.get(user_id)

        if user is not None:
            del util.verify_dict[user_id]
            return user

    return None


class Nerodia:

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="connectreddit")
    @commands.check(dm_only)
    @commands.cooldown(rate=2, per=5. * 60, type=BucketType.user)
    async def connect_reddit(self, ctx):
        """Connects your Discord account to your reddit account.

        This command can only be used in private messages
        to prevent other people connecting their reddit account
        to your Discord ID, for whatever reason.
        """

        await ctx.trigger_typing()

        if sub_db.get_reddit_name(ctx.message.author.id) is not None:
            return await ctx.send(embed=ALREADY_CONNECTED_EMBED)
        elif not isinstance(ctx.message.channel, discord.abc.PrivateChannel):
            return await ctx.send(embed=DM_ONLY_EMBED)

        token = secrets.token_urlsafe()
        await ctx.send(embed=create_instructions(token))

        author_id = str(ctx.message.author.id)
        util.token_dict[author_id] = token

        reddit_name = await wait_for_add(author_id)
        del util.token_dict[author_id]

        if reddit_name is None:
            await ctx.send(embed=NO_PM_IN_TIME_EMBED)
        else:
            db_session.add(
                DRConnection(discord_id=ctx.message.author.id, reddit_name=reddit_name)
            )
            db_session.commit()
            await ctx.send(
                embed=discord.Embed(
                    title="Verified successfully:",
                    description=f"Your reddit name is {reddit_name}!",
                    colour=discord.Colour.green(),
                )
            )

    @commands.command(name="disconnectreddit")
    async def disconnect_reddit(self, ctx):
        """
        Disconnects your reddit account from your Discord account.
        """

        await ctx.trigger_typing()
        author = db_session.query(DRConnection).filter_by(
            discord_id=ctx.message.author.id
        ).first()

        if author is None:
            return await ctx.send(
                embed=discord.Embed(
                    title="Failed to disconnect:",
                    description="You do not have an account connected.",
                    colour=discord.Colour.red(),
                )
            )
        else:
            db_session.delete(author)
            return await ctx.send(
                embed=discord.Embed(
                    title="Disconnected!",
                    description="Your reddit account was successfully "
                    "disconnected from your Discord ID.",
                    colour=discord.Colour.green(),
                )
            )

    @commands.command(aliases=["db"])
    async def dashboard(self, ctx, subreddit_name: str = None):
        """A dashboard for information about a connected reddit account

        To get a dashboard on a per-subreddit basis,
        use `db subname`, for example `db askreddit`.

        This command requires you to have a reddit
        account connected to your Discord ID through
        the `connectreddit` command.
        """

        await ctx.trigger_typing()

        reddit_name = sub_db.get_reddit_name(ctx.message.author.id)
        if reddit_name is None:
            await ctx.send(embed=NO_CONNECTION_EMBED)
        elif subreddit_name is not None:
            if sub_db.exists(subreddit_name):
                await ctx.send(
                    embed=discord.Embed(colour=discord.Colour.blue()).set_author(
                        name=f"Dashboard for {subreddit_name}",
                        url=f"https://reddit.com/r/{subreddit_name}",
                    ).add_field(
                        name="Subreddit Moderators",
                        value="• "
                        + "\n• ".join(
                            r.name for r in reddit.subreddit(subreddit_name).moderator()
                        ),
                    ).add_field(
                        name="Followed Streams",
                        value="• " + "\n• ".join(sub_db.get_follows(subreddit_name)),
                    )
                )
            else:
                await ctx.send(embed=UNKNOWN_SUBREDDIT_EMBED)
        else:
            modded_sub_list = "\n• ".join(sub_db.get_modded_subs(reddit_name))
            if modded_sub_list:
                moderated_subs = "• " + modded_sub_list
            else:
                moderated_subs = "*No known moderated Subreddits* :("

            await ctx.send(
                embed=discord.Embed(colour=discord.Colour.blue()).set_author(
                    name=f"Dashboard for {reddit_name}",
                    url=f"https://reddit.com/u/{reddit_name}",
                    icon_url=ctx.message.author.avatar_url,
                ).add_field(
                    name="Moderated Subreddits", value=moderated_subs, inline=False
                )
            )

    @commands.command(name="gdb")
    @commands.guild_only()
    async def guild_dashboard(self, ctx):
        """A dashboard for information about the Guild.

        Shows which streams the guild
        this is invoked on is following.
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
    async def sfollow(self, ctx, subreddit_name: str, *stream_names: str):
        """Follows the given stream with the given subreddit name.
        Of course, this only works if you are a moderator on the given subreddit.
        Also supports passing a list of stream names, for example:
            `n!sfollow mysubreddit stream1 stream2 stream3`
        Only stream names for streams that exist will be followed.
        The streams where the bot could not validate will be shown
        in the bot's response, so you can check if you made any mistakes.

        Following a stream effectively means that the Bot will update
        the specified Subreddit's sidebar whenever the Stream goes
        online or offline in order to keep the subreddit updated.
        """

        await ctx.trigger_typing()

        reddit_name = sub_db.get_reddit_name(ctx.message.author.id)
        if reddit_name is None:
            return await ctx.send(embed=NO_CONNECTION_EMBED)
        elif not sub_db.exists(subreddit_name):
            return await ctx.send(embed=UNKNOWN_SUBREDDIT_EMBED)

        sub_moderators = reddit.subreddit(subreddit_name).moderator()
        if reddit_name not in sub_moderators:
            return await ctx.send(embed=USER_NOT_MODERATOR_EMBED)
        elif BOT_REDDIT_NAME not in sub_moderators:
            return await ctx.send(
                embed=BOT_NOT_MODERATOR_EMBED.add_field(
                    name="Invite me as a Moderator:",
                    value=f"https://reddit.com/r/{subreddit_name}/about/moderators/\n"
                    "This is required so that I can update your sidebar.\n"
                    f"My reddit name is **`{BOT_REDDIT_NAME}`**.",
                )
            )

        valid_streams = [
            s for s in stream_names if await twitch.get_user(s) is not None
        ]
        present_follows = sub_db.get_follows(subreddit_name)
        unique_streams = set(s for s in valid_streams if s not in present_follows)

        await sub_db.follow(subreddit_name, *unique_streams)
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
    async def gfollow(self, ctx, *stream_names: str):
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
    async def sunfollow(self, ctx, subreddit_name: str, *stream_names: str):
        """Unfollows the given streams on the given Subreddit.
        Of course, you must
        be a Moderator on the Subreddit to
        use this command. Like the follow
        command, this support passing a list
        of stream names, for example:
            `n!sunfollow imaqtpie discordapp`
        Unfollowing a stream means that the
        bot will no longer update the given
        subreddit's sidebar when the stream
        goes online or offline.
        """

        await ctx.trigger_typing()

        reddit_name = sub_db.get_reddit_name(ctx.message.author.id)
        if reddit_name is None:
            return await ctx.send(embed=NO_CONNECTION_EMBED)
        elif not sub_db.exists(subreddit_name):
            return await ctx.send(embed=UNKNOWN_SUBREDDIT_EMBED)
        elif reddit_name not in reddit.subreddit(subreddit_name).moderator():
            return await ctx.send(embed=USER_NOT_MODERATOR_EMBED)

        unique_streams = set(stream_names)
        old_follows = sub_db.get_follows(subreddit_name)
        unfollowed = [s for s in unique_streams if s in old_follows]
        await sub_db.unfollow(subreddit_name, *unique_streams)

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
    async def gunfollow(self, ctx, *stream_names: str):
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

    bot.add_cog(Nerodia(bot))
    log.info("Added main cog to the Discord bot.")
