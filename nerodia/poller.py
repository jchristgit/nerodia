"""
Contains various functions related
to the Twitch API. It is recommended
to use the various related functions
of the database module instead of
these, since these always execute
an API call while the database module
tries to obtain data from the SQLite
database before making any queries.

The functions in this module are
threadsafe using locks.
"""

from typing import Optional

from . import database as db
from .apis.twitch import TwitchUser
from .clients import twitch


async def get_user_info(stream_name: str) -> Optional[TwitchUser]:
    """
    Returns a TwitchUser containing a properly cased
    name for the given stream name as well as its ID,
    which is used for making various API requests.
    If the user is not found, returns None.

    Arguments:
        stream_name (str): The name of the stream to look up.

    Returns:
        Optional[TwitchUser]: When the stream exists, a named tuple with
                              various keys returned from the API is
                              returned. Please view `TwitchUser` in the
                              `apis/twitch.py` module for further information.
                              When it does not exist, returns `None`.
    """

    return await twitch.get_user_info_by_name(stream_name)


async def is_online(stream_name: str) -> bool:
    """
    Checks whether the given stream is online.
    It is highly recommended to validate that
    a stream exists before running this function,
    as it will not perform any checks.

    Arguments:
        stream_name (str): The stream name for which to check

    Returns:
        bool: Whether the stream under the given ID is online.
    """

    stream_id = await db.get_stream_id(stream_name)
    return await twitch.get_stream_by_user(stream_id) is not None
