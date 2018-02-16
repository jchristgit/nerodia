"""
Provides common database queries
as functions for both the Discord
and the Reddit interface.
"""

from ..clients import twitch
from .models import session, Follow


def is_followed(stream_name: str) -> bool:
    """
    Checks whether a given stream is followed
    by either a Subreddit or a Guild.

    Arguments:
        stream_name (str):
            The stream which should be checked.

    Returns:
        bool:
            Whether a Subreddit or Guild follows the stream or not.
    """

    res = session.query(Follow) \
        .filter(Follow.follows == stream_name) \
        .first()
    if res is not None:
        return True
    return False


async def follow_if_new(*stream_names: str):
    """
    Subscribes to events for given streams
    if they are not subscribed to yet.

    Arguments:
        stream_names (str):
            The streams to conditionally subscribe to.
    """

    for name in stream_names:
        if not is_followed(name):
            stream = await twitch.get_user(name)
            await twitch.sub_stream(stream['id'])


async def unfollow_if_unused(*stream_names: str):
    """
    Unsubscribes from events for the given
    streams if they are no longer of interest.

    Arguments:
        stream_names (str):
            The streams to conditionally unsubscribe from.
    """

    for name in stream_names:
        if not is_followed(name):
            stream = await twitch.get_user(name)
            await twitch.unsub_stream(stream['id'])
