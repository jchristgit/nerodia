import discord

from nerodia.clients import twitch as twitch_client
from nerodia.twitch import TwitchStream


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
