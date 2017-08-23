"""
Contains various constants that
are used in the various cogs,
mainly embeds that are sent when
various errors occur, for example
with the discord <=> reddit
connection authentication, or
various other issues.
"""

import discord

from ..clients import reddit
from ..util import reddit_lock

with reddit_lock:
    BOT_REDDIT_NAME = reddit.user.me()

ALREADY_CONNECTED_EMBED = discord.Embed(
    title="Cannot connect accounts:",
    description="You already have a reddit account connected. "
                "Use the `disconnectreddit` command to disconnect "
                "your Discord account from your reddit account.",
    colour=discord.Colour.orange()
)
BOT_NOT_MODERATOR_EMBED = discord.Embed(
    title="Cannot perform operation on Subreddit:",
    description="I need to be Moderator on the Subreddit for this to work.",
    colour=discord.Colour.red()
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
UNKNOWN_SUBREDDIT_EMBED = discord.Embed(
    title="Failed to execute Command:",
    description="The Subreddit you passed to the command does not appear to exist.",
    colour=discord.Colour.red()
)
USER_NOT_MODERATOR_EMBED = discord.Embed(
    title="Failed to change Subreddit settings:",
    description="You need to be a Moderator on the Subreddit to use this Command.",
    colour=discord.Colour.red()
)
PM_URL = "https://www.reddit.com/message/compose?to=Botyy&subject=verification&message="

# The timeout for the reddit verification, in minutes
VERIFY_TIMEOUT = 5
