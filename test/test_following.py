import unittest

from nerodia import database as db
from nerodia.models import session, Subreddit


class TwoFollowsTestCase(unittest.TestCase):
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
        (ID column omitted)
              name   |   follows
            ---------+--------------
            test-sub | test-stream
            test-sub | test-stream-2
        This is cleaned up again in `tearDown`,
        given that the `unfollow` method
        functions properly (further test runs
        would have more than two rows if this
        would happen, although unlikely)
        """

        db.follow("test-sub", "test-stream", "test-stream-2")

    def tearDown(self):
        """
        Removes the previously added subreddit
        "test-sub" from the subreddit table
        along with the two streams it followed.
        """

        db.unfollow("test-sub", "test-stream", "test-stream-2")

    def test_sub_follows_streams(self):
        """
        Validates that the subreddit "test-sub"
        follows the two streams "test-stream" and
        "test-stream-2" as set up in `setUp`.
        """

        self.assertListEqual(
            db.get_subreddit_follows("test-sub"), ["test-stream", "test-stream-2"]
        )
        self.assertEqual(len(session.query(Subreddit).all()), 2)

    def test_unknown_sub_no_follows(self):
        """
        Validates that an unknown subreddit
        does not follow any streams.
        """

        self.assertListEqual(db.get_subreddit_follows("unknown-sub"), [])

    def test_all_follows(self):
        """
        Validates that obtaining all follows
        returns a Generator, resulting in a list
        of the two followed streams "test-stream"
        and "test-stream-2"
        """

        self.assertListEqual(
            db.get_all_follows(), ["test-stream", "test-stream-2"]
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
