"""
Provides functions for
common database queries
revolving around Discord guilds.
"""

from typing import Optional, List

from . import models as db


def get_follows(guild_id: int) -> List[str]:
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


def follow(guild_id: int, *stream_names: str):
    """
    Follows the given argument list of streams
    with the given Discord guild.

    Arguments:
        guild_id (int):
            The Guild ID which should follow the given argument list of streams.
        stream_names (str):
            An argument list of stream names to follow.
    """

    db.session.add_all(
        db.Follow(stream, guild_id=guild_id) for stream in stream_names
    )
    db.session.commit()


def unfollow(guild_id: int, *stream_names: str):
    """
    Unfollow the given argument list of streams
    on the Discord Guild with the given ID.

    Arguments:
        guild_id (int):
            The Discord Guild ID for the guild on which the
            given argument list of streams should be unfollowed.
        stream_names (str):
            An argument list of stream names to unfollow.
    """

    db.session.query(db.Follow) \
        .filter(db.Follow.guild_id == guild_id) \
        .filter(db.Follow.follows.in_(stream_names)) \
        .delete(synchronize_session='fetch')
    db.session.commit()


def set_update_channel(guild_id: int, channel_id: int):
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


def unset_update_channel(guild_id: int):
    """
    Unsets the stream announcement
    channel for the given Guild ID.

    Arguments:
        guild_id (int):
            The guild ID for which the stream
            update announcement channel should
            be unset.
    """

    db.session.query(db.UpdateChannel) \
        .filter(db.UpdateChannel.guild_id == guild_id) \
        .delete(synchronize_session='fetch')


def get_update_channel(guild_id: int) -> Optional[int]:
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
