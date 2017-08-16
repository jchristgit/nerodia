"""
Contains the command group
for the Discord Bot.
"""

import asyncio
import datetime
import discord
from typing import Optional

from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

from . import util
from . import database as db
from .util import (
    remove_token,
    token_dict, token_lock,
    verify_dict, verify_lock
)


ALREADY_CONNECTED_EMBED = discord.Embed(
    title="Cannot connect accounts:",
    description="You already have a reddit account connected. "
                "Use the `disconnectreddit` command to disconnect "
                "your Discord account from your reddit account.",
    colour=discord.Colour.orange()
)
DM_ONLY_EMBED = discord.Embed(
    title="Cannot connect accounts:",
    description="For safety reasons, this command can "
                "only be used in private messages.",
    colour=discord.Colour.red()
)
NO_CONNECTION_EMBED = discord.Embed(
    title="Failed to run command:",
    description="This command requires you to have a reddit account "
                "connected through the `connectreddit` command.",
    colour=discord.Colour.red()
)
NO_PM_IN_TIME_EMBED = discord.Embed(
    title="Failed to verify:",
    description="No verification PM was received in time.",
    colour=discord.Colour.red()
)
NOT_MODERATOR_EMBED = discord.Embed(
    title="Failed to change Subreddit settings:",
    description="You need to be a Moderator on the Subreddit to use this Command.",
    colour=discord.Colour.red()
)
UNKNOWN_SUBREDDIT_EMBED = discord.Embed(
    title="Failed to execute Command:",
    description="The Subreddit you passed to the command does not appear to exist.",
    colour=discord.Colour.red()
)

PM_URL = "https://www.reddit.com/message/compose?to=Botyy&subject=verification&message="

# The timeout for the reddit verification, in minutes
VERIFY_TIMEOUT = 5


def create_instructions(token: str) -> discord.Embed:
    """
    Creates an Embed containing the disclaimer
    for adding a Reddit account to your Discord account.
    This should be used for adding a field with the token
    which the user should send to the bot via a direct message.

    Arguments:
        token (str): The token that should be appended to the reddit PM link.

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
              "time, along with your reddit name, and this information "
              "may appear in the bot's log messages**. You can "
              "disconnect a connected account at any time.",
        inline=False
    ).add_field(
        name="Warning",
        value="**Do not share this link!**"
    ).add_field(
        name="Instructions",
        value=f"Send me a [Reddit Message]({PM_URL + token}) by clicking on "
              f"the link and clicking `send` to connect your reddit account.",
    ).set_footer(
        text="⏲ You have five minutes of time before the token expires."
    )


async def wait_for_add(user_id: str, timeout: int = VERIFY_TIMEOUT) -> Optional[str]:
    """
    Waits for the given user to add his reddit
    account. It is highly recommended to set
    a timeout, this defaults to five minutes.
    The dictionary which contains data about
    verification is checked in intervals,
    accomplished by sleeping for five seconds
    between checking the dictionary.

    Arguments:
        user_id (str):
            The Discord user ID for the user
            who wants to add his reddit account.
        timeout (int):
            The timeout (in minutes) after which
            `None` should be returned indicating
            that the user did not send a direct
            message for adding his reddit account
            in time. The user is removed from the
            verification dictionary. Defaults to
            the value of `VERIFY_TIMEOUT`.

    Returns:
        Optional[str]:
            The reddit name of the user if successful,
            `None` if no valid direct message containing
            the token was received in time.
    """

    timeout_ctr = timeout * 60
    while timeout_ctr > 0:
        await asyncio.sleep(5)
        timeout_ctr -= 5
        with verify_lock:
            user = verify_dict.get(user_id)

        if user is not None:
            with verify_lock:
                del verify_dict[user_id]

            return user

    return None


class Nerodia:
    """
    Commands for interacting with the Nerodia reddit bot.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        print("[DISCORD] Loaded Commands.")

    @commands.command(name="connectreddit")
    @commands.cooldown(rate=2, per=5. * 60, type=BucketType.user)
    async def connect_reddit(self, ctx):
        """
        Connects your Discord account to your reddit account.
        Please make sure to carefully read through the
        disclaimer and  the instructions that this
        command sends upon invocation.

        If you already have a reddit account connected,
        please use the `disconnectreddit` command to
        remove your reddit account from the database.

        This command can only be used in private messages
        to prevent other people connecting their reddit account
        to your Discord ID, for whatever reason.
        """

        await ctx.trigger_typing()

        if not isinstance(ctx.message.channel, discord.abc.PrivateChannel):
            return await ctx.send(embed=DM_ONLY_EMBED)
        elif db.get_reddit_name(ctx.message.author.id) is not None:
            return await ctx.send(embed=ALREADY_CONNECTED_EMBED)

        token = util.random_string()
        await ctx.send(embed=create_instructions(token))

        author_id = str(ctx.message.author.id)
        with token_lock:
            token_dict[author_id] = token

        reddit_name = await wait_for_add(author_id)
        remove_token(author_id)

        if reddit_name is None:
            await ctx.send(embed=NO_PM_IN_TIME_EMBED)
        else:
            db.add_dr_connection(ctx.message.author.id, reddit_name)
            await ctx.send(embed=discord.Embed(
                title="Verified successfully:",
                description=f"Your reddit name is {reddit_name}!",
                colour=discord.Colour.green()
            ))

    @commands.command()
    async def disconnectreddit(self, ctx):
        """
        Disconnects your reddit account from
        your Discord account, if connected.
        """

        await ctx.trigger_typing()

        if db.get_reddit_name(ctx.message.author.id) is None:
            return await ctx.send(embed=discord.Embed(
                title="Failed to disconnect:",
                description="You do not have an account connected.",
                colour=discord.Colour.red()
            ))
        else:
            db.remove_dr_connection(ctx.message.author.id)
            return await ctx.send(embed=discord.Embed(
                title="Disconnected!",
                description="Your reddit account was successfully "
                            "disconnected from your Discord ID.",
                colour=discord.Colour.green()
            ))

    @commands.group(aliases=["db"])
    async def dashboard(self, ctx, subreddit_name: str=None):
        """
        Displays a dashboard for all information
        about a connected reddit account, such as
        which subreddits you moderate.

        To get a dashboard on a per-subreddit basis,
        use `db subname`, for example `db askreddit`.

        This command requires you to have a reddit
        account connected to your Discord ID through
        the `connectreddit` command.
        """

        await ctx.trigger_typing()

        reddit_name = db.get_reddit_name(ctx.message.author.id)
        if reddit_name is None:
            await ctx.send(embed=NO_CONNECTION_EMBED)
        elif subreddit_name is not None:
            if db.subreddit_exists(subreddit_name):
                await ctx.send(embed=discord.Embed(
                    colour=discord.Colour.blue()
                ).set_author(
                    name=f"Dashboard for {subreddit_name}",
                    url=f"https://reddit.com/r/{subreddit_name}"
                ).add_field(
                    name="Subreddit Moderators",
                    value='• ' + '\n• '.join(
                        r.name for r in db.get_subreddit_moderators(subreddit_name)
                    )
                ).add_field(
                    name="Followed Streams",
                    value='• ' + '\n• '.join(db.get_subreddit_follows(subreddit_name))
                ))
            else:
                await ctx.send(embed=UNKNOWN_SUBREDDIT_EMBED)
        else:
            modded_sub_list = '\n'.join(db.get_moderated_subreddits(reddit_name))
            if modded_sub_list:
                moderated_subs = "• " + modded_sub_list
            else:
                moderated_subs = "*No known moderated Subreddits* :("

            await ctx.send(embed=discord.Embed(
                colour=discord.Colour.blue()
            ).set_author(
                name=f"Dashboard for {reddit_name}",
                url=f"https://reddit.com/u/{reddit_name}",
                icon_url=ctx.message.author.avatar_url
            ).add_field(
                name="Moderated Subreddits",
                value=moderated_subs,
                inline=False
            ))

    @commands.command()
    async def follow(self, ctx, subreddit_name: str, *stream_names: str):
        """
        Follows the given stream with the given subreddit name.
        Of course, this only works if you are a moderator on the given subreddit.
        Also supports passing a list of stream names, for example:
            `follow imaqtpie bardmains discordapp`
        Only stream names for streams that exist will be followed.
        The streams where the bot could not validate will be shown
        in the bot's response, so you can check if you made any mistakes.

        Following a stream effectively means that the Bot will update
        the specified Subreddit's sidebar whenever the Stream goes
        online or offline in order to keep the subreddit updated.
        """

        await ctx.trigger_typing()

        reddit_name = db.get_reddit_name(ctx.message.author.id)
        if reddit_name is None:
            return await ctx.send(embed=NO_CONNECTION_EMBED)
        elif not db.subreddit_exists(subreddit_name):
            return await ctx.send(embed=UNKNOWN_SUBREDDIT_EMBED)
        elif reddit_name not in db.get_subreddit_moderators(subreddit_name):
            return await ctx.send(embed=NOT_MODERATOR_EMBED)

        valid_streams = (s for s in stream_names if db.stream_exists(s))
        present_follows = db.get_subreddit_follows(subreddit_name)
        unique_streams = set(s for s in valid_streams if s not in present_follows)

        db.follow(subreddit_name, *unique_streams)
        await ctx.send(embed=discord.Embed(
            title="Follow command",
            colour=discord.Colour.blue(),
            timestamp=datetime.datetime.now()
        ).add_field(
            name="Newly followed:",
            value='• ' + '\n• '.join(unique_streams)
        ).add_field(
            name="Failed to follow:",
            value='• ' + '\n• '.join(s for s in stream_names if s not in unique_streams)
        ))

    @commands.command()
    async def unfollow(self, ctx, subreddit_name: str, *stream_names: str):
        """
        Unfollows the given streams on the
        given Subreddit. Of course, you must
        be a Moderator on the Subreddit to
        use this command. Like the follow
        command, this support passing a list
        of stream names, for example:
            `unfollow imaqtpie discordapp`
        Unfollowing a stream means that the
        bot will no longer update the given
        subreddit's sidebar when the stream
        goes online or offline.
        """

        await ctx.trigger_typing()

        reddit_name = db.get_reddit_name(ctx.message.author.id)
        if reddit_name is None:
            return await ctx.send(embed=NO_CONNECTION_EMBED)
        elif not db.subreddit_exists(subreddit_name):
            return await ctx.send(embed=UNKNOWN_SUBREDDIT_EMBED)
        elif reddit_name not in db.get_subreddit_moderators(subreddit_name):
            return await ctx.send(embed=NOT_MODERATOR_EMBED)

        unique_streams = set(stream_names)
        old_follows = db.get_subreddit_follows(subreddit_name)
        unfollowed = [s for s in unique_streams if s in old_follows]
        db.unfollow(subreddit_name, *unique_streams)

        await ctx.send(embed=discord.Embed(
            title="Unfollow complete",
            colour=discord.Colour.blue()
        ).add_field(
            name="Unfollowed Streams",
            value='• ' + '\n •'.join(unfollowed)
        ).add_field(
            name="Failed to unfollow",
            value='• ' + '\n •'.join(s for s in unique_streams if s not in unfollowed)
        ))


def setup(bot: commands.Bot):
    """
    Adds the nerodia command
    group to the discord bot.
    """

    bot.add_cog(Nerodia(bot))
