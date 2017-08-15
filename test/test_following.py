import unittest

from . import setup

setup.init()

from nerodia import database as db  # noqa
from nerodia.models import session, Subreddit  # noqa


class DatabaseFollowingTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass


setup.finish()
