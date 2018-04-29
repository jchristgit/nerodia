import discord

from nerodia.twitch import TwitchStream, TwitchUser


def create_stream_online_embed(stream: TwitchStream, user: TwitchUser) -> discord.Embed:
    """Formats stream information for an online stream into an Embed.

    Args:
        stream (TwitchStream):
            The stream for which the Embed should be created.
        user (TwitchUser):
            The user that is streaming.

    Returns:
        discord.Embed:
            A nicely formatted embed with
            information about the given stream.
    """

    stream_url = f"https://twitch.tv/{user.name}"
    result = discord.Embed(
        title=f"{user.name} is now live!",
        url=stream_url,
        description=f"{stream_url}\n\n*{stream.title}*",
        colour=0x722AA4,
    )
    result.set_image(url=user.offline_image_url)
    result.set_thumbnail(url=user.profile_image_url)
    return result
