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

from . import setup
setup.init()
# pylint: disable=wrong-import-position
from nerodia import models as db  # noqa


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
    assert isinstance(stream.followed_by.all(), list)
    assert isinstance(stream.added_on, datetime.datetime)

    assert stream.name == "test-stream"
    assert stream.id == 1337
    assert stream.followed_by.all() == []
    assert stream.added_on > ONE_MINUTE_AGO
    assert stream.added_on < datetime.datetime.now()

    db.session.rollback()


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
    assert isinstance(sub.all_follows.all(), list)

    assert sub.name == "test-sub"
    assert sub.follows == "test-stream"
    assert sub.all_follows.all() == []

    db.session.rollback()


def test_adds_stream():
    """
    Validates that a new stream
    is added properly and queries
    return the stream.
    """

    new_stream = db.Stream(name="good-games", id=1000)
    db.session.add(new_stream)

    assert db.session.query(db.Stream).first() == new_stream
    assert new_stream in db.session.query(db.Stream).all()
    assert db.session.query(db.Stream).filter_by(name="good-games").first() == new_stream
    assert db.session.query(db.Stream).filter_by(id=1000).first() == new_stream

    db.session.rollback()


def test_adds_subreddit():
    """
    Similiar to the above function,
    this validates that a new
    subreddit is added properly and
    queries return the subreddit.
    """

    new_sub = db.Subreddit(name="some-sub", follows="unknown-stream")
    db.session.add(new_sub)

    assert db.session.query(db.Subreddit).first() == new_sub
    assert new_sub in db.session.query(db.Subreddit).all()
    assert db.session.query(db.Subreddit).filter_by(name="some-sub").first() == new_sub
    assert db.session.query(db.Subreddit).filter_by(follows="unknown-stream").first() == new_sub

    db.session.rollback()


setup.finish()
