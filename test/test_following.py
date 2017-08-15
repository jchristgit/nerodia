import unittest

from nerodia import database as db
from nerodia.models import session, Subreddit


class DatabaseFollowingTestCase(unittest.TestCase):
    def setUp(self):
        db.follow("test-sub", "test-stream", "test-stream-2")

    def tearDown(self):
        db.unfollow("test-sub", "test-stream", "test-stream-2")

    def test_sub_follows_streams(self):
        """
        Validates that the subreddit "test-sub"
        follows the two streams "test-stream" and
        "test-stream-2" as set up in `setUp`.
        """

        self.assertListEqual(db.get_subreddit_follows("test-sub"), ["test-stream", "test-stream-2"])
        self.assertEqual(len(session.query(Subreddit).all()), 2)

    def test_unknown_sub_no_follows(self):
        """
        Validates that an unknown subreddit
        does not follow any streams.
        """

        self.assertListEqual(db.get_subreddit_follows("unknown-sub"), [])
