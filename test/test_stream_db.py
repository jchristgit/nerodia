"""
Tests the various functions
exposed in database.py which
are used to get data from the
databases before making an API
call to either the Reddit
or the Twitch API.
"""

import unittest

from nerodia import database as db


class StreamDatabaseTestCase(unittest.TestCase):
    def setUp(self):
        """This test does not require any setup."""

    def tearDown(self):
        """Nothing was created in `setUp`, thus this function does nothing."""

    def test_stream_id(self):
        """
        Validates that trying to get
        the stream ID for an unknown
        stream returns None, and returns
        an integer for an existing stream.
        """

        self.assertIsInstance(db.get_stream_id("volcyy"), int)

        self.assertIsNone(db.get_stream_id("definitelyunknownstreamthatwillneverexist"))
