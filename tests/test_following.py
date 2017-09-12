"""
Contains various tests related to
subreddits following various streams.

The test cases set up different relationships
between the subreddits and the follows,
for example without any follow, or with
one subreddit and multiple follows.

The proper function of these modules
is vital to the bot working properly,
as a malfunction might lead to messed
up sidebars or not followed streams
being put onto an unrelated sidebar.
"""

import unittest

from nerodia import database as db
from nerodia.models import session, Follow


class TwoFollowsOneSubredditTestCase(unittest.TestCase):
    """
    A test case for validating that various
    follow-related functions return a list
    of two streams as well as empty lists
    for various queries after adding a single
    subreddit that is following two streams
    to the database.
    """

    def setUp(self):
        """
        Adds two rows to the Subreddit table,
        looking somewhat like the following
        This is cleaned up again in `tearDown`,
        given that the `unfollow` method
        functions properly (further test runs
        would have more than two rows if this
        would happen, although unlikely).
        """

        db.subreddit_follow("test-sub", "test-stream", "test-stream-2")

    def tearDown(self):
        """
        Removes the previously added subreddit
        "test-sub" from the subreddit table
        along with the two streams it followed.
        """

        db.subreddit_unfollow("test-sub", "test-stream", "test-stream-2")

    def test_sub_follows_streams(self):
        """
        Validates that the subreddit "test-sub"
        follows the two streams "test-stream" and
        "test-stream-2" as set up in `setUp`.
        """

        self.assertListEqual(
            db.get_subreddit_follows("test-sub"), ["test-stream", "test-stream-2"]
        )
        self.assertEqual(len(session.query(Follow).all()), 2)

    def test_unknown_sub_no_follows(self):
        """
        Validates that an unknown subreddit
        does not follow any streams.
        """

        self.assertListEqual(db.get_subreddit_follows("unknown-sub"), [])

    def test_all_follows(self):
        """
        Validates that obtaining all follows
        returns a list of the two followed
        streams "test-stream" and "test-stream-2".
        """

        self.assertListEqual(
            db.get_all_follows(), ["test-stream", "test-stream-2"]
        )

    def test_get_subs_following(self):
        """
        Validates that the get_subreddits_following
        function properly returns a list of subreddit
        names that are following the given stream.
        """

        self.assertListEqual(
            db.get_subreddits_following("test-stream"), ["test-sub"]
        )
        self.assertListEqual(
            db.get_subreddits_following("test-stream-2"), ["test-sub"]
        )
        self.assertListEqual(
            db.get_subreddits_following("unknown-stream"), []
        )
        self.assertListEqual(
            db.get_subreddits_following(""), []
        )


class EmptyFollowsTestCase(unittest.TestCase):
    """
    A test case for validating that
    various follow-related methods
    return an empty list when no
    entries are present in the database.
    """

    def setUp(self):
        """
        Adds nothing, since we are testing
        for the result of various methods
        when no rows are in the database.
        """

    def tearDown(self):
        """
        Since nothing needs to be cleaned
        up, this method does nothing.
        """

    def test_sub_follows_no_streams(self):
        """
        Validates that querying the database
        for the follows of any subreddit
        results in an empty list.
        """

        self.assertListEqual(
            db.get_subreddit_follows("test"), []
        )
        self.assertListEqual(
            db.get_subreddit_follows("unknown-sub"), []
        )

    def test_all_follows_empty(self):
        """
        Validates that calling get_all_follows
        results in an empty list as there are
        no follows in the database.
        """

        self.assertListEqual(
            db.get_all_follows(), []
        )

    def test_get_subs_following(self):
        """
        Validates that the get_subreddits_following
        function returns empty lists for any queries
        ran against it, considering that we did not
        add any follows to the database in this test case.
        """

        self.assertListEqual(
            db.get_subreddits_following("test-stream"), []
        )
        self.assertListEqual(
            db.get_subreddits_following("unknown-stream"), []
        )
        self.assertListEqual(
            db.get_subreddits_following(""), []
        )


class SubredditAndGuildTwoUniqueFollowsTestCase(unittest.TestCase):
    """
    A test case which validates that the
    follow-related functions correctly
    return unique results when a Discord
    Guild and a Subreddit follow a total
    of three streams, where they share
    the same follow, namely `test-stream-2`.
    """

    def setUp(self):
        """
        Sets up a total of three follows:
        - The Subreddit `test-sub` follows
          the streams `test-stream` and
          `test-stream-2`.
        - The Guild `test-guild` follows
          the stream `test-stream-2`.
        """

        db.subreddit_follow("test-sub", "test-stream", "test-stream-2")
        db.guild_follow(1337, "test-stream-2")

    def tearDown(self):
        """
        Removes the previously created
        follows from the Subreddit
        `test-sub` and the guild `test-guild`.
        """

        db.subreddit_unfollow("test-sub", "test-stream", "test-stream-2")
        db.guild_unfollow(1337, "test-stream-2")

    def test_get_all_follows(self):
        """
        Validates that `get_all_follows`
        properly returns a list of a
        total of 2 unique elements,
        namely `test-stream` and
        `test-stream-2`.

        Since the updater task should only
        poll unique entries, this is vital
        in order to not spam the API with
        unnecessary requests, since the
        handlers for the stream update
        dispatch the stream update event
        to a handler for editing the sidebar
        on the following Subreddits as
        well as a handler for sending the
        update to the Discord guild's
        stream announcement channel.
        """

        all_follows = db.get_all_follows()

        self.assertEqual(len(all_follows), 2)
        self.assertListEqual(all_follows, ["test-stream", "test-stream-2"])

    def test_get_guild_follows(self):
        """
        Validates that the `get_guild_follows`
        function is not influenced by the
        added streams to the subreddit, and
        returns a single element as expected.
        """

        guild_follows = db.get_guild_follows(1337)

        self.assertEqual(len(guild_follows), 1)
        self.assertListEqual(guild_follows, ["test-stream-2"])

    def test_get_subreddit_follows(self):
        """
        Validates that the `get_subreddit_follows`
        function is not influenced by the
        added streams to the Discord Guild, and
        returns two elements as expected.
        """

        sub_follows = db.get_subreddit_follows("test-sub")

        self.assertEqual(len(sub_follows), 2)
        self.assertListEqual(sub_follows, ["test-stream", "test-stream-2"])
