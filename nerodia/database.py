"""
Abstracts receiving data from
the SQLite database, and polling
for data from Reddit or Twitch
when the data is not stored yet.

All database operations are
threadsafe using a lock.
"""

import functools
from typing import Generator, List, Optional

from praw.models import RedditorList
from prawcore.exceptions import NotFound

from . import models as db
from .clients import reddit, twitch


async def get_stream_id(stream_name: str) -> Optional[int]:
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
        user = await twitch.get_user_info_by_name(stream_name)
        if user is None:
            return None
        db.session.add(db.Stream(name=user.name, id=user.id))
        return user.id

    return db_stream.id


async def stream_exists(stream_name: str) -> bool:
    """
    Returns a boolean indicating whether the
    given stream exists or not.

    Arguments:
        stream_name (str): The Stream that should be looked up.

    Returns:
        bool: Whether the given Stream exists.
    """

    return await get_stream_id(stream_name) is not None


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

    db_sub = db.session.query(db.Follow) \
        .filter(db.Follow.sub_name == subreddit_name) \
        .first()
    if db_sub is None:
        try:
            reddit.subreddits.search_by_name(subreddit_name, exact=True)
        except NotFound:
            return False
    return True


@functools.lru_cache()
def get_subreddit_moderators(subreddit_name: str) -> RedditorList:
    """
    Returns a list of Moderators for the given Subreddit.
    If the Subreddit was not found, returns None.
    Results from up to 128 recent calls are cached.
    It is recommended to first validate that the
    Subreddit exists, which is usually preferable anyways.

    Arguments:
        subreddit_name (str):
            The Subreddit for which Moderators should be returned.

    Returns:
        RedditorList:
            A list of `Redditor`s that moderate the subreddit.
    """

    return reddit.subreddit(subreddit_name).moderator()


def add_dr_connection(discord_id: int, reddit_name: str):
    """
    Adds a row to the DRConnection table.

    Arguments:
        discord_id (int): The Discord ID of the user who invoked a command.
        reddit_name (str): The reddit name of the user.
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
        Generator[str, None, None]:
            A generator of subreddit names, for example `askreddit` or `pics`.
    """

    # Since SQLAlchemy returns a list of tuples when querying for a single
    # attribute, such as `db.Subreddit.name` in this case, we flatten the
    # list using a generator so we have a list of known subreddits.
    all_subs = (
        n.sub_name for n in
        db.session.query(db.Follow.sub_name)
        .filter(db.Follow.sub_name.isnot(None))
        .distinct()
    )
    return (
        sub_name
        for sub_name in all_subs
        if reddit_name in (r.name for r in get_subreddit_moderators(sub_name))
    )


def get_subreddit_follows(sub_name: str) -> List[str]:
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

    # As above, we flatten the result of the query since SQLAlchemy
    # returns the result as a list of tuples with a single element.
    result = db.session.query(db.Follow.follows) \
        .filter(db.Follow.sub_name == sub_name)
    return [s for row_tuple in result for s in row_tuple]


def get_guild_follows(guild_id: int) -> List[str]:
    """
    Returns a list of Twitch stream names which
    the given Discord Guild ID is following.

    Arguments:
        guild_id (int):
            The Guild for which to obtain the follows.

    Returns:
        List[str]:
            A list of Twitch stream names that the guild is following.
    """

    result = db.session.query(db.Follow.follows) \
        .filter(db.Follow.guild_id == guild_id)
    return [s for row_tuple in result for s in row_tuple]


def get_subreddits_following(stream_name: str) -> List[str]:
    """
    Returns a list of subreddits that are following the
    given stream.

    Arguments:
        stream_name (str): The stream which followers should be returned.

    Returns:
        List[str]: A list of subreddits that are following the stream.
    """

    result = db.session.query(db.Follow.sub_name) \
        .filter(db.Follow.sub_name.isnot(None)) \
        .filter(db.Follow.follows == stream_name)
    return [s.sub_name for s in result]


def get_guilds_following(stream_name: str) -> List[int]:
    """
    Returns a list of Discord guilds - specifically,
    their IDs - that are following the given stream.

    Arguments:
        stream_name (str): The stream name which followers should be returned.

    Returns:
        List[int]: A list of Discord guild IDs following the given stream.
    """

    result = db.session.query(db.Follow.guild_id) \
        .filter(db.Follow.guild_id.isnot(None)) \
        .filter(db.Follow.follows == stream_name)
    return [g.guild_id for g in result]


def subreddit_follow(subreddit_name: str, *stream_names: str):
    """
    Follows the given argument list of streams
    with the given subreddit. Make sure to validate
    the identity of whoever invokes the function
    as a Moderator of the Subreddit before calling it.

    This adds a total of len(stream_names) rows in the following format
    to the database, where stream_name is an element of stream_names:
        subreddit_name | stream_name

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


def guild_follow(guild_id: int, *stream_names: str):
    """
    Follows the given argument list of streams
    with the given Discord guild.

    For further information, view the
    docstring for `subreddit_exists` above.

    Arguments:
        guild_id (int):
            The Guild ID which should follow the given argument list of streams.
        stream_names (str):
            An argument list of stream names that should be followed.
    """

    db.session.add_all(
        db.Follow(stream, guild_id=guild_id) for stream in stream_names
    )
    db.session.commit()


def subreddit_unfollow(subreddit_name: str, *stream_names: str):
    """
    Unfollows the given argument list of streams
    with the given subreddit. As for the follow
    function, make sure to validate the identity
    of whoever invokes the function as a Moderator
    of the given subreddit before calling it.

    If the Subreddit is unknown, this will not
    change anything. Additionally, when streams
    are passed that the Subreddit is not following,
    nothing will happen either, since the rows
    are filtered before the operation is performed.

    Arguments:
        subreddit_name (str):
            The Subreddit for which the given streams should be unfollowed.
        stream_names (str):
            An argument list of stream names that should be unfollowed,
            if they are being followed at the time this function is called.
    """

    db.session.query(db.Follow) \
        .filter(db.Follow.sub_name == subreddit_name) \
        .filter(db.Follow.follows.in_(stream_names)) \
        .delete(synchronize_session='fetch')
    db.session.commit()


def guild_unfollow(guild_id: int, *stream_names: str):
    """
    Unfollow the given argument list of streams
    on the Discord Guild with the given ID.

    Look at the docstring for `subreddit_follow`
    for further information about this.


    Arguments:
        guild_id (int):
            The Discord Guild ID for the guild on which the
            given argument list of streams should be unfollowed.
        stream_names (str):
            An argument list of stream names which should
            be unfollowed, given that they are being followed
            when this function is called.
    """

    db.session.query(db.Follow) \
        .filter(db.Follow.guild_id == guild_id) \
        .filter(db.Follow.follows.in_(stream_names)) \
        .delete(synchronize_session='fetch')
    db.session.commit()


def set_guild_update_channel(guild_id: int, channel_id: int):
    """
    Sets the stream announcement channel
    for the given Guild ID to the given
    channel ID, resulting in all stream
    updates for streams that the guild
    is following to be posted in it.

    Arguments:
        guild_id (int):
            The guild for which the channel should be set.
        channel_id (int):
            The channel ID for the channel in which the
            stream update announcements should be posted.
    """

    db.session.add(db.UpdateChannel(
        guild_id=guild_id, channel_id=channel_id)
    )
    db.session.commit()


def unset_guild_update_channel(guild_id: int):
    """
    Unsets the stream announcement
    channel for the given Guild ID.
    Does nothing if the guild has
    no stream update announcement
    channel set.

    Arguments:
        guild_id (int):
            The guild ID for which the stream
            update announcement channel should
            be unset.
    """

    db.session.query(db.UpdateChannel) \
        .filter(db.UpdateChannel.guild_id == guild_id) \
        .delete(synchronize_session='fetch')


def get_guild_update_channel(guild_id: int) -> Optional[int]:
    """
    Gets the channel ID in which stream announcements
    should be posted for the given Guild ID.

    Arguments:
        guild_id (int):
            The Discord guild ID for which the stream
            update channel ID should be returned.

    Returns:
        Optional[int]:
            The channel ID for the stream update channel,
            or `None` if no channel was set.
    """

    result = db.session.query(db.UpdateChannel) \
        .filter(db.UpdateChannel.guild_id == guild_id) \
        .first()

    if result is not None:
        return result.channel_id
    return None


def get_all_follows() -> List[str]:
    """
    Gets a list of all streams that are
    being followed by various Subreddits
    and Discord guilds.

    Returns:
        List[str]:
            A list of unique streams that are
            being followed by various subreddits,
            as well as Discord guilds.
    """

    result = db.session.query(db.Follow.follows) \
        .distinct()
    return [row.follows for row in result]
