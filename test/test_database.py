"""
Tests the various functions
exposed in database.py which
are used to get data from the
databases before making an API
call to either the Reddit
or the Twitch API.
"""

from . import setup
from praw.models import Redditor, RedditorList

setup.init()

from nerodia import database as db  # noqa
from nerodia.models import session, Subreddit  # noqa


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


def test_get_subreddit_moderators():
    """
    Validates that the get_subreddit_moderators
    function properly returns a list of Moderators
    for the given Subreddit, and `None` if the
    Subreddit was not found.
    """

    zero_mods = db.get_subreddit_moderators("deadsub")
    assert len(zero_mods) == 0

    three_mods = db.get_subreddit_moderators("bottiquette")
    assert len(three_mods) == 3
    assert isinstance(three_mods, RedditorList)
    assert all(isinstance(mod, Redditor) for mod in three_mods)


def test_get_moderated_subreddits():
    """
    Validates that the get_moderated_subreddits
    function properly returns a generator of
    subreddits that a given User moderates,
    given the condition that the subreddits
    exist inside the bot's database.
    """

    session.add(Subreddit(
        name="test",
        follows="test-stream"
    ))

    assert "test" in [ms for ms in db.get_moderated_subreddits("xvvhiteboy")]

    session.add(Subreddit(
        name="UFOs",
        follows="test-stream"
    ))

    assert [ms for ms in db.get_moderated_subreddits("xvvhiteboy")] == ["test", "UFOs"]

    session.rollback()


setup.finish()
