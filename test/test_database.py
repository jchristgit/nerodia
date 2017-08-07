"""
Tests the database models.
This sets a custom environment
variable for the database to
ensure that the actual database
is not changed through the run.
The environment variable is
reset when the tests are done.
"""

import datetime
import os

OLD_DB_PATH = os.environ.get('NERODIA_DB_PATH')
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.abspath(os.path.join(TEST_DIR, os.pardir))
TEST_DB_PATH = os.path.join(
    PARENT_DIR, "test", "test.db"
)
os.environ['NERODIA_DB_PATH'] = TEST_DB_PATH

from nerodia import database as db  # pylint: disable=wrong-import-position


ONE_MINUTE_AGO = datetime.datetime.now() - datetime.timedelta(minutes=1)


def test_stream_columns():
    """
    Validates that the rows in the
    Stream table have the
    correct types and values.
    """

    new_stream = db.Stream(name="test-stream", id=1337)
    db.session.add(new_stream)
    stream = db.session.query(db.Stream).first()

    assert isinstance(stream.name, str)
    assert isinstance(stream.id, int)
    assert isinstance(stream.subreddits.all(), list)
    assert isinstance(stream.added_on, datetime.datetime)

    assert stream.name == "test-stream"
    assert stream.id == 1337
    assert stream.subreddits.all() == []
    assert stream.added_on > ONE_MINUTE_AGO
    assert stream.added_on < datetime.datetime.now()


def test_subreddit_columns():
    """
    Validates that the rows in the
    Subreddit table have the
    correct types and values.
    """

    new_sub = db.Subreddit(name="test-sub", follows="test-stream")
    db.session.add(new_sub)
    sub = db.session.query(db.Subreddit).first()

    assert isinstance(sub.id, int)
    assert isinstance(sub.name, str)
    assert isinstance(sub.streams.all(), list)

    assert sub.name == "test-sub"
    assert sub.follows == "test-stream"
    assert sub.streams.all() == []
