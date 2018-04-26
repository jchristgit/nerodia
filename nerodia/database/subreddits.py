"""
Contains functions for
common database queries
for the Reddit interface.
"""

import functools
from typing import Generator, Optional, List

from prawcore.exceptions import NotFound

from . import models as db
from ..clients import reddit


def get_reddit_name(discord_id: int) -> Optional[str]:
    """
    Returns the reddit name for the given
    Discord ID, or `None` if no database
    entry for the Discord ID exists.

    Arguments:
        discord_id (int):
            The Discord ID for the user whose reddit name should be returned.
    Returns:
        Optional[str]:
            The reddit name associated with the given Discord ID.
    """

    user = db.session.query(db.DRConnection).filter(
        db.DRConnection.discord_id == discord_id
    ).first()
    if user is not None:
        return user.reddit_name
    return None


@functools.lru_cache(maxsize=32)
def exists(subreddit_name: str) -> bool:
    """
    Returns a boolean indicating whether the
    given Subreddit exists.

    Arguments:
        subreddit_name (str):
            The Subreddit which existence shall be checked.
    Returns:
        bool:
            Whether the Subreddit exists or not.
    """

    db_sub = db.session.query(db.Follow).filter(
        db.Follow.sub_name == subreddit_name
    ).first()
    if db_sub is None:
        try:
            reddit.subreddits.search_by_name(subreddit_name, exact=True)
        except NotFound:
            return False
    return True


def get_follows(sub_name: str) -> List[str]:
    """
    Returns a List of Twitch stream names
    that the given subreddit is following.

    Arguments:
        sub_name (str):
            The Subreddit for which to obtain the follows.
    Returns:
        List[str]:
            A list of Twitch stream names that the subreddit is following.
    """

    result = db.session.query(db.Follow.follows).filter(db.Follow.sub_name == sub_name)
    return [s for row_tuple in result for s in row_tuple]


def get_modded_subs(reddit_name: str) -> Generator[str, None, None]:
    """
    Returns a generator of known Subreddits
    that the given Redditor moderates.

    Arguments:
        reddit_name (str):
            The Redditor whose moderated subreddits should be returned.
    Returns:
        Generator[str, None, None]:
            A generator of subreddit names, for example `askreddit` or `pics`.
    """

    all_subs = (
        n.sub_name
        for n in db.session.query(db.Follow.sub_name).filter(
            db.Follow.sub_name.isnot(None)
        ).distinct()
    )
    return (
        sub_name
        for sub_name in all_subs
        if reddit_name in (r.name for r in reddit.subreddit(sub_name).moderator())
    )


async def follow(subreddit_name: str, *stream_names: str):
    """
    Follows the given argument list of streams
    with the given subreddit.

    Arguments:
        subreddit_name (str):
            The Subreddit for which the given streams should be followed.
        stream_names (str):
            An argument list of stream names that should be followed.
    """

    db.session.add_all(
        db.Follow(stream, sub_name=subreddit_name) for stream in stream_names
    )
    db.session.commit()


async def unfollow(subreddit_name: str, *stream_names: str):
    """
    Unfollows the given argument list of streams
    with the given subreddit.

    Arguments:
        subreddit_name (str):
            The Subreddit for which the given streams should be unfollowed.
        stream_names (str):
            An argument list of stream names that should be unfollowed,
            if they are being followed at the time this function is called.
    """

    db.session.query(db.Follow).filter(db.Follow.sub_name == subreddit_name).filter(
        db.Follow.follows.in_(stream_names)
    ).delete(
        synchronize_session="fetch"
    )
    db.session.commit()
