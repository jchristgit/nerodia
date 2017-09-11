"""
Tests the various functions
exposed in database.py which
are used to get data from the
databases before making an API
call to either the Reddit
or the Twitch API.
"""

import asyncio
import unittest

from nerodia import database as db


class StreamDatabaseTestCase(unittest.TestCase):
    def setUp(self):
        """Sets up an event loop for running coroutines."""

        self.loop = asyncio.get_event_loop()

    def tearDown(self):
        """Cleans up the event loop."""

        self.loop.close()

    def test_stream_id(self):
        """
        Validates that trying to get
        the stream ID for an unknown
        stream returns None, and returns
        an integer for an existing stream.
        """

        known_stream_id = self.loop.run_until_complete(db.get_stream_id("volcyy"))
        self.assertIsInstance(known_stream_id, int)

        future = db.get_stream_id("definitelyunknownstreamthatwillneverexist")
        unknown_stream_id = self.loop.run_until_complete(future)
        self.assertIsNone(unknown_stream_id)
