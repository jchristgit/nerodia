from .twitch import TwitchClient, TwitchStream

from discord import Embed


async def create_stream_online_embed(
    user_name: str, stream: TwitchStream, twitch_client: TwitchClient
) -> Embed:
    """Formats stream information for an online stream into an Embed.

    Args:
        user_name (str):
            The username associated with the stream.
        stream (TwitchStream):
            The stream for which the Embed should be created.
        twitch_client (TwitchClient):
            An instance of the asynchronous Twitch client.

    Returns:
        discord.Embed:
            A nicely formatted embed with
            information about the given stream.
    """

    stream_url = f"https://twitch.tv/{user_name}"
    result = Embed(
        title=f"{user_name} is now live!",
        url=stream_url,
        description=f"{stream_url}\n\n*{stream.title}*",
        colour=0x722AA4,
    )
    result.set_image(url=stream.thumbnail_url)
    user = await twitch_client.get_user(user_name)
    result.set_thumbnail(url=user.avatar_url)
    return result
