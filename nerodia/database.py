"""
Abstracts receiving data from
the SQLite database, and polling
for data from Reddit or Twitch
when the data is not stored yet.
"""

import functools
from typing import Generator, Optional

from praw.models import RedditorList
from prawcore.exceptions import NotFound

from . import models as db
from . import poller
from .workers import reddit


@functools.lru_cache(maxsize=32)
def get_stream_id(stream_name: str) -> Optional[int]:
    """
    Attempts to obtain the stream ID for the
    given Stream name from the database. If
    it is not found, executes an API call.
    If the API call returns `None`, the stream
    does not exist and this function will return
    None. Otherwise, the newly added stream ID
    will be added to the database and returned.

    Arguments:
        stream_name (str):
            The Stream for which to the ID should be obtained.

    Returns:
        Optional[int]:
            The stream ID if the stream exists, None otherwise.
    """

    db_stream = db.session.query(db.Stream).\
        filter(db.Stream.name.ilike(stream_name)).\
        first()

    if db_stream is None:
        user = poller.get_user_info(stream_name)
        if user is None:
            return None
        stream_id = int(user.id)
        db.session.add(db.Stream(name=user.name, stream_id=stream_id))
        return stream_id

    return db_stream.stream_id


def stream_exists(stream_name: str) -> bool:
    """
    Returns a boolean indicating whether the
    given stream exists or not.

    Arguments:
        stream_name (str): The Stream that should be looked up.

    Returns:
        bool: Whether the given Stream exists.
    """

    return get_stream_id(stream_name) is not None


@functools.lru_cache(maxsize=32)
def subreddit_exists(subreddit_name: str) -> bool:
    """
    Returns a boolean indicating whether the
    given Subreddit exists. Checks the Subreddit
    database table for any entries first.
    Up to 32 recent calls are cached.

    Arguments:
        subreddit_name (str):
            The Subreddit which existence shall be checked.

    Returns:
        bool:
            Whether the Subreddit exists or not.
    """

    db_sub = db.session.query(db.Subreddit.name.ilike(subreddit_name)).first()
    if db_sub is None:
        try:
            reddit.subreddits.search_by_name(subreddit_name, exact=True)
        except NotFound:
            return False
    return True


@functools.lru_cache()
def get_subreddit_moderators(subreddit_name: str) -> Optional[RedditorList]:
    """
    Returns a list of Moderators for the given Subreddit.
    If the Subreddit was not found, returns None.
    Results from up to 128 recent calls are cached.

    Arguments:
        subreddit_name (str):
            The Subreddit for which Moderators should be returned.

    Returns:
        Optional[RedditorList]:
            A list of `Redditor`s that moderate the subreddit.
            `None` if the subreddit was not found
    """

    if not subreddit_exists(subreddit_name):
        return None
    else:
        return reddit.subreddit(subreddit_name).moderator()


def add_dr_connection(discord_id: int, reddit_name: str):
    """
    Adds a row to the DRConnection table.

    Arguments:
        discord_id (int): The Discord ID of the user who invoked a command.
        reddit_name (str): The reddit name of the user.

    Notes:
        Since this function is only called on the
        main thread (in the discord Bot, specifically
        the Nerodia cog), this does not use
        any locking mechanism.
    """

    db.session.add(db.DRConnection(discord_id=discord_id, reddit_name=reddit_name))
    db.session.commit()


def remove_dr_connection(discord_id: int):
    """
    Removes a discord ID | reddit name
    "connection" (row) from the database.

    Arguments:
        discord_id (int): the discord ID of the mapping to be removed
    """

    db.session.query(db.DRConnection) \
        .filter(db.DRConnection.discord_id == discord_id) \
        .delete()
    db.session.commit()


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

    Note:
        To check whether the user has a reddit account
        associated with them, simply check whether the returned
        value of this function is `None`.
    """

    user = db.session.query(db.DRConnection) \
        .filter(db.DRConnection.discord_id == discord_id) \
        .first()
    if user is not None:
        return user.reddit_name
    return None


def get_moderated_subreddits(reddit_name: str) -> Generator[str, None, None]:
    """
    Returns a generator of Subreddits that the given
    reddit user is known to moderate by the
    database contents, since (from what I know)
    the reddit API does not provide any means
    of obtaining the moderated subreddits of a redditor.

    Arguments:
        reddit_name (str):
            The Redditor whose moderated subreddits should be returned.

    Returns:
        Generator[str]:
            A generator of subreddit names, for example `askreddit` or `pics`.
    """

    # Since SQLAlchemy returns a list of tuples when querying for a single
    # attribute, such as `db.Subreddit.name` in this case, we flatten the
    # list using a generator so we have a list of known subreddits.
    all_subs = (
        n for name_tuple in db.session.query(db.Subreddit.name).all() for n in name_tuple
    )
    return (
        sub_name
        for sub_name in all_subs
        if reddit_name in (r.name for r in get_subreddit_moderators(sub_name))
    )
