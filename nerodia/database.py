"""
Handles receiving data from
the SQLite database, and polling
for data from Reddit or Twitch
when the data is not stored yet.
"""

import functools
from typing import Optional

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
        stream_name (str): The Stream for which to
                           the ID should be obtained.

    Returns:
        Optional[int]: The stream ID if the stream
                       exists, None otherwise.
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


@functools.lru_cache(maxsize=32)
def subreddit_exists(subreddit_name: str) -> bool:
    """
    Returns a boolean indicating whether the
    given Subreddit exists. Checks the Subreddit
    database table for any entries first.
    Up to 32 recent calls are cached.
    """

    db_sub = db.session.query(db.Subreddit.name.ilike(subreddit_name)).first()
    if db_sub is None:
        try:
            reddit.subreddits.search_by_name(subreddit_name, exact=True)
        except NotFound:
            return False
    return True


@functools.lru_cache(maxsize=128)
def get_subreddit_moderators(subreddit_name: str) -> Optional[RedditorList]:
    """
    Returns a list of Moderators for the given Subreddit.
    If the Subreddit was not found, returns None.
    Results from up to 128 recent calls are cached.
    """

    if not subreddit_exists(subreddit_name):
        return None
    else:
        return reddit.subreddit(subreddit_name).moderator()
