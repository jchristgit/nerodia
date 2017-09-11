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

from collections import namedtuple
from typing import Optional

from .clients import twitch


TwitchUser = namedtuple("TwitchUser", "name id")


def get_user_info(stream_name: str) -> Optional[TwitchUser]:
    """
    Returns a TwitchUser containing a properly cased
    name for the given stream name as well as its ID,
    which is used for making various API requests.
    If the user is not found, returns None.

    Arguments:
        stream_name (str): The name of the stream to look up.

    Returns:
        Optional[TwitchUser]: When the stream exists, a named tuple with
                              the attributes `name` and `id` is returned.
                              When it does not exist, returns `None`.
    """

    user = twitch.users.translate_usernames_to_ids(stream_name)
    if not user:
        return None
    return TwitchUser(name=user[0].name, id=user[0].id)


def is_online(stream_name: str) -> bool:
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

    user = get_user_info(stream_name)
    return twitch.streams.get_stream_by_user(user.id) is not None
