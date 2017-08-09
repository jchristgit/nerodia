"""
Tests the various functions
exposed in database.py which
are used to get data from the
databases before making an API
call to either the Reddit
or the Twitch API.
"""

from . import setup
setup.init()

from nerodia import database as db


def test_unknown_stream():
    """
    Validates that trying to get
    the stream ID for an unknown
    stream returns None.
    """

    assert db.get_stream_id("definitelyunknownstreamthatwillneverexist") is None


def test_known_stream():
    """
    Validates that getting the
    stream ID for a known
    stream returns an integer.
    """

    stream_id = db.get_stream_id("volcyy")
    assert isinstance(stream_id, int)


def test_subreddit_exists():
    """
    Validates that the subreddit
    exists function properly returns
    ``True`` or ``False`` with existing
    and unknown subreddits.
    """

    assert db.subreddit_exists("all")
    assert db.subreddit_exists("askreddit")
    assert db.subreddit_exists("pics")

    assert not db.subreddit_exists("thisdefinitelydoesnotexist")
    assert not db.subreddit_exists("123912i0491528190518")
    assert not db.subreddit_exists("anotherunknownsubreddit")


setup.finish()
