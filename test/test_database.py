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

print(db.get_stream_id("volcyy"))

setup.finish()
