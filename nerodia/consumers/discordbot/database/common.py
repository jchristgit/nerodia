"""
Provides common database queries
as functions for both the Discord
and the Reddit interface.
"""

from typing import List

from .models import session, Follow


def is_followed(stream_name: str) -> bool:
    """Checks whether a given stream is followed by either a Subreddit or a Guild.

    Args:
        stream_name (str):
            The stream which should be checked.

    Returns:
        bool:
            Whether a Subreddit or Guild follows the stream or not.
    """

    res = session.query(Follow).filter(Follow.follows == stream_name).first()
    return res is not None


def get_all_follows() -> List[str]:
    """Gets all follows present in the `Follow` database.

    Returns:
        List[str]:
            A list of Twitch names of followed streams.
    """

    return [row[0] for row in session.query(Follow.follows).distinct().all()]
