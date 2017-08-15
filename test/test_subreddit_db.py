
import unittest

from praw.models import RedditorList, Redditor

from nerodia import database as db  # noqa
from nerodia.models import session, Subreddit  # noqa


class SubredditDatabaseTestCase(unittest.TestCase):
    def setUp(self):
        """
        Adds a single Subreddit named "test" following
        a stream called "test-stream". It is deleted when done.
        """

        session.add(Subreddit(
            name="test",
            follows="test-stream"
        ))

    def tearDown(self):
        """
        Removes the previously added Subreddit "test"
        following a stream called "test-stream".
        """

        session.query(Subreddit) \
            .filter(Subreddit.name == "test") \
            .filter(Subreddit.follows == "test-stream") \
            .delete()

    def test_subreddit_exists(self):
        """
        Validates that the subreddit
        exists function properly returns
        ``True`` or ``False`` with existing
        and unknown subreddits.
        """

        self.assertTrue(db.subreddit_exists("all"))
        self.assertTrue(db.subreddit_exists("askreddit"))
        self.assertTrue(db.subreddit_exists("pics"))

        self.assertFalse(db.subreddit_exists("thisdefinitelydoesnotexist"))
        self.assertFalse(db.subreddit_exists("123912i0491528190518"))
        self.assertFalse(db.subreddit_exists("anotherunknownsubreddit"))

    def test_get_subreddit_moderators(self):
        """
        Validates that the get_subreddit_moderators
        function properly returns a list of Moderators
        for the given Subreddit, and `None` if the
        Subreddit was not found.
        """

        zero_mods = db.get_subreddit_moderators("deadsub")
        self.assertEqual(len(zero_mods), 0)

        three_mods = db.get_subreddit_moderators("bottiquette")
        self.assertEqual(len(three_mods), 3)
        self.assertIsInstance(three_mods, RedditorList)
        for mod in three_mods:
            self.assertIsInstance(mod, Redditor)

    def test_get_moderated_subreddits(self):
        """
        Validates that the get_moderated_subreddits
        function properly returns a generator of
        subreddits that a given User moderates,
        given the condition that the subreddits
        exist inside the bot's database.
        """

        self.assertIn(
            "test", [ms for ms in db.get_moderated_subreddits("xvvhiteboy")]
        )
        self.assertEqual(
            [ms for ms in db.get_moderated_subreddits("xvvhiteboy")], ["test"]
        )
