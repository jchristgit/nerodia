"""
Tests the stream update announcement channel
which is used for the Discord Bot to
announce Twitch streams going online and offline,
given that the Guild is following the stream.
"""

import unittest

from sqlalchemy import and_, or_

from nerodia import database as db, models


TEST_CHANNEL_ID_ONE = 9876
TEST_CHANNEL_ID_TWO = 8765
TEST_GUILD_ID_ONE = 1234
TEST_GUILD_ID_TWO = 2345


class EmptyUpdateChannels(unittest.TestCase):
    """
    A test case for various database functions
    related to the stream update announcement
    channel database.

    This test case validates that the functions
    properly return nothing when the database
    is queried without any entries.
    """

    def setUp(self):
        """No setup necessary, since the database stays empty."""

    def tearDown(self):
        """No teardown necessary, did not add anything in `setUp`."""

    def test_get_guild_update_channel(self):
        """
        Validates that `get_guild_update_channel`
        returns `None` for various queries.
        """

        self.assertIsNone(db.get_guild_update_channel(0))
        self.assertIsNone(db.get_guild_update_channel(913))


class SingleUpdateChannelTestCase(unittest.TestCase):
    """
    Another test case for various database functions
    related to the stream update announcement channel database.

    In this test case, an update channel is added for a single guild.

    This test case modifies the session directly instead of using
    the functions of the database module
    in the `setUp` and `tearDown` methods.
    """

    def setUp(self):
        """Add a single `UpdateChannel` row to be used in tests."""

        models.session.add(models.UpdateChannel(
            guild_id=TEST_GUILD_ID_ONE, channel_id=TEST_CHANNEL_ID_ONE
        ))
        models.session.commit()

    def tearDown(self):
        """Removes the previously added `UpdateChannel` row."""

        models.session.query(models.UpdateChannel) \
            .filter(models.UpdateChannel.guild_id == TEST_GUILD_ID_ONE) \
            .filter(models.UpdateChannel.channel_id == TEST_CHANNEL_ID_ONE) \
            .delete(synchronize_session='fetch')
        models.session.commit()

    def test_get_guild_update_channel(self):
        """
        Validates that `get_guild_update_channel` properly
        returns `None` for any unknown guild ID and the
        previously set channel ID for the `UpdateChannel`
        row which was added in `setUp`.
        """

        self.assertEqual(
            db.get_guild_update_channel(TEST_GUILD_ID_ONE), TEST_CHANNEL_ID_ONE
        )

        self.assertIsNone(db.get_guild_update_channel(0))
        self.assertIsNone(db.get_guild_update_channel(400))


class TwoUpdateChannelsTestCase(unittest.TestCase):
    """
    A test case with two update channels
    on two different guilds.
    """

    def setUp(self):
        """
        Adds two `UpdateChannel`s for
        use in the various test methods.
        """

        models.session.add_all((models.UpdateChannel(
            guild_id=TEST_GUILD_ID_ONE, channel_id=TEST_CHANNEL_ID_ONE
        ), models.UpdateChannel(
            guild_id=TEST_GUILD_ID_TWO, channel_id=TEST_CHANNEL_ID_TWO
        )))
        models.session.commit()

    def tearDown(self):
        """
        Removes all entries from the
        tables that were added in `setUp`
        """

        models.session.query(models.UpdateChannel) \
            .filter(or_(
                and_(
                    models.UpdateChannel.guild_id == TEST_GUILD_ID_ONE,
                    models.UpdateChannel.channel_id == TEST_CHANNEL_ID_ONE
                ),
                and_(
                    models.UpdateChannel.guild_id == TEST_GUILD_ID_TWO,
                    models.UpdateChannel.channel_id == TEST_CHANNEL_ID_TWO
                )
            )) \
            .delete(synchronize_session='fetch')
        models.session.commit()

    def test_get_guild_update_channel(self):
        """
        Tests that retrieving the guild update channel
        returns entries as expected for both guilds.
        """

        self.assertEqual(db.get_guild_update_channel(TEST_GUILD_ID_ONE), TEST_CHANNEL_ID_ONE)
        self.assertEqual(db.get_guild_update_channel(TEST_GUILD_ID_TWO), TEST_CHANNEL_ID_TWO)

        self.assertIsNone(db.get_guild_update_channel(0))
        self.assertIsNone(db.get_guild_update_channel(300))


class SetUpdateChannelTestCase(unittest.TestCase):
    """
    Tests the proper function of the `set_guild_update_channel`
    and `unset_guild_update_channel` functions.
    """

    def setUp(self):
        """
        Sets the guild update channels for two guilds, defined by
        `TEST_GUILD_ID_ONE`, `TEST_GUILD_ID_TWO`, as well as
        `TEST_CHANNEL_ID_ONE` and `TEST_CHANNEL_ID_TWO`.
        """

        db.set_guild_update_channel(TEST_GUILD_ID_ONE, TEST_CHANNEL_ID_ONE)
        db.set_guild_update_channel(TEST_GUILD_ID_TWO, TEST_CHANNEL_ID_TWO)

    def tearDown(self):
        """Cleans up any previously set test update channels."""

        models.session.query(models.UpdateChannel) \
            .filter(or_(
                and_(
                    models.UpdateChannel.guild_id == TEST_GUILD_ID_ONE,
                    models.UpdateChannel.channel_id == TEST_CHANNEL_ID_ONE
                ),
                and_(
                    models.UpdateChannel.guild_id == TEST_GUILD_ID_TWO,
                    models.UpdateChannel.channel_id == TEST_CHANNEL_ID_TWO
                )
            )) \
            .delete(synchronize_session='fetch')
        models.session.commit()

    def test_get_guild_update_channel(self):
        """
        Validates that `set_guild_update_channel` properly added
        two `UpdateChannel`s in `setUp`.
        """

        self.assertEqual(db.get_guild_update_channel(TEST_GUILD_ID_ONE), TEST_CHANNEL_ID_ONE)
        self.assertEqual(db.get_guild_update_channel(TEST_GUILD_ID_TWO), TEST_CHANNEL_ID_TWO)


class UnsetUpdateChannelTestCase(unittest.TestCase):
    """
    Tests the proper function of the
    `unset_guild_update_channel` method.
    """

    def setUp(self):
        """
        Adds two rows like of `UpdateChannel`s, then
        removes them using `unset_guild_update_channel`.
        The test methods validate if this succeeded, and
        `tearDown` cleans up `UpdateChannel`s if necessary.
        """

        models.session.add_all((models.UpdateChannel(
            guild_id=TEST_GUILD_ID_ONE, channel_id=TEST_CHANNEL_ID_ONE
        ), models.UpdateChannel(
            guild_id=TEST_GUILD_ID_TWO, channel_id=TEST_CHANNEL_ID_TWO
        )))
        models.session.commit()

        db.unset_guild_update_channel(TEST_GUILD_ID_ONE)
        db.unset_guild_update_channel(TEST_GUILD_ID_TWO)

    def tearDown(self):
        """Removes any leftovers from the tests."""

        models.session.query(models.UpdateChannel) \
            .filter(or_(
                and_(
                    models.UpdateChannel.guild_id == TEST_GUILD_ID_ONE,
                    models.UpdateChannel.channel_id == TEST_CHANNEL_ID_ONE
                ),
                and_(
                    models.UpdateChannel.guild_id == TEST_GUILD_ID_TWO,
                    models.UpdateChannel.channel_id == TEST_CHANNEL_ID_TWO
                )
            )) \
            .delete(synchronize_session='fetch')
        models.session.commit()

    def test_total_rows_is_0(self):
        """Validates that there are no more rows in the table."""

        self.assertEqual(
            len(models.session.query(models.UpdateChannel).all()), 0
        )

    def test_get_guild_update_channel_returns_none(self):
        """Validates that `get_guild_update_channel` now returns `None`"""

        self.assertIsNone(db.get_guild_update_channel(TEST_GUILD_ID_ONE))
        self.assertIsNone(db.get_guild_update_channel(TEST_GUILD_ID_TWO))
