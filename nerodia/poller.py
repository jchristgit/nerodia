from collections import namedtuple
from typing import Optional, Union

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


def is_online(stream: str) -> bool:
    """
    Checks whether the given stream is online.
    It is highly recommended to validate that
    a stream exists before running this function,
    as it will not perform any checks.

    Arguments:
        stream_id (str): The stream name for which to check

    Returns:
        bool: Whether the stream under the given ID is online.
    """

    return twitch.streams.get_stream_by_user(get_user_info(stream).id) is not None
