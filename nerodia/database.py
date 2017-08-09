"""
Handles receiving data from
the SQLite database, and polling
for data from Reddit or Twitch
when the data is not stored yet.
"""

from typing import List, Optional

from . import models as db
from . import poller
from .workers import reddit


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
        db.session.add(db.Stream(name=user.name, stream_id=user.id))
        return user.id

    return db_stream.stream_id


def subreddit_exists(subreddit_name: str) -> bool:
    """
    Returns a boolean indicating whether the
    given Subreddit exists. Checks the Subreddit
    database table for any entries first.
    """


def get_subreddit_moderators(subreddit_name: str) -> Optional[List[str]]:
    """
    Returns a list of Moderators for the given Subreddit.
    If the Subreddit was not found, returns None.
    """
