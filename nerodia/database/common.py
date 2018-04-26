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
    return res is not None
