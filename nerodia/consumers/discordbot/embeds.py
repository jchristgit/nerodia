import discord

from clients import twitch as twitch_client
from twitch import TwitchStream


async def create_stream_online_embed(user_name: str, stream: TwitchStream) -> discord.Embed:
    """Formats stream information for an online stream into an Embed.

    Args:
        user_name (str):
            The username associated with the stream.
        stream (TwitchStream):
            The stream for which the Embed should be created.

    Returns:
        discord.Embed:
            A nicely formatted embed with
            information about the given stream.
    """

    stream_url = f"https://twitch.tv/{user_name}"
    result = discord.Embed(
        title=f"{user_name} is now live!",
        url=stream_url,
        description=f"{stream_url}\n\n*{stream.title}*",
        colour=0x722AA4,
    )
    result.set_image(url=stream.thumbnail_url)
    user = await twitch_client.get_user(user_name)
    result.set_thumbnail(url=user.profile_image_url)
    return result


ALREADY_CONNECTED_EMBED = discord.Embed(
    title="Cannot connect accounts:",
    description="You already have a reddit account connected. "
    "Use the `disconnectreddit` command to disconnect "
    "your Discord account from your reddit account.",
    colour=discord.Colour.orange(),
)
BOT_NOT_MODERATOR_EMBED = discord.Embed(
    title="Cannot perform operation on Subreddit:",
    description="I need to be Moderator on the Subreddit for this to work.",
    colour=discord.Colour.red(),
)
DM_ONLY_EMBED = discord.Embed(
    title="Cannot connect accounts:",
    description="For safety reasons, this command can "
    "only be used in private messages.",
    colour=discord.Colour.red(),
)
NO_CONNECTION_EMBED = discord.Embed(
    title="Failed to run command:",
    description="This command requires you to have a reddit account "
    "connected through the `connectreddit` command.",
    colour=discord.Colour.red(),
)
NO_PM_IN_TIME_EMBED = discord.Embed(
    title="Failed to verify:",
    description="No verification PM was received in time.",
    colour=discord.Colour.red(),
)
UNKNOWN_SUBREDDIT_EMBED = discord.Embed(
    title="Failed to execute Command:",
    description="The Subreddit you passed to the command does not appear to exist.",
    colour=discord.Colour.red(),
)
USER_NOT_MODERATOR_EMBED = discord.Embed(
    title="Failed to change Subreddit settings:",
    description="You need to be a Moderator on the Subreddit to use this Command.",
    colour=discord.Colour.red(),
)