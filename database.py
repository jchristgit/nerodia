from typing import Generator, NamedTuple

import dataset


class FollowedStream(NamedTuple):  # pylint: disable=too-few-public-methods
    """
    A custom NamedTuple that contains
    the name and the ID of a followed
    stream in the database.
    """

    name: str
    id: int  # pylint: disable=invalid-name

DB = dataset.connect("sqlite:///data/nerodia.db")

# The Streams, with an ID and a name.
STREAMS = DB['streams']

# The follows, organized by subreddit.
FOLLOWS = DB['follows']


def all_follows() -> Generator[FollowedStream, None, None]:
    """
    Returns a generator of all streams being
    followed in the FollowedStream named tuple.
    The ID is the stream ID as an integer, and
    the name is the stream name as a string.

    Example:
        >>> for follow in all_follows():
        ...     print(f"{follow.name}: {follow.id}")
    """

    return (FollowedStream(row['name'], row['id']) for row in STREAMS)


def follow_stream(subreddit_name: str, stream_name: str) -> None:
    """
    Creates database entries for the given
    `subreddit_name` to follow the stream
    given by `stream_name`. This will cause
    the subreddit's sidebar to be updated
    when the stream goes online or offline.

    It must be validated that the stream
    exists before using this function.

    Example with other functions:
        >>> follow_stream("SomeSubreddit", "SomeStreamer")
        >>> list(sub_follows("SomeSubreddit"))
        ["SomeStreamer"]
        >>> unfollow_stream("SomeSubreddit", "SomeStreamer")
    """

    FOLLOWS.upsert(dict(
        subreddit=subreddit_name,
        stream=stream_name
    ), ['subreddit', 'stream'])


def unfollow_stream(subreddit_name: str, stream_name: str) -> None:
    """
    Unfollows the given Stream.
    Results in the subreddit no
    longer receiving updates
    about the stream going online
    or offline in its sidebar.

    This assumes that the subreddit
    was following the stream before-
    hand, but nothing will happen
    if it did not beforehand.
    """

    FOLLOWS.delete(
        subreddit=subreddit_name,
        stream=stream_name
    )


def sub_follows(subreddit_name: str) -> Generator[str]:
    """
    Gets all stream names that the given
    subreddit is following as a generator.
    """

    return (row['stream'] for row in FOLLOWS.find(subreddit=subreddit_name))
