"""
Database file. Contains the table
classes and relationships for
the Subreddit as well as the Stream
tables. Each subreddit can follow
0 - n streams, and each stream can
be folloed by 0 - n subreddits, thus
resulting in a many - to - many
relationship between the two tables.

By default, the database file is
created under the filename "nerodia.db"
in the directory in which the application
is run. If you wish to change this
behaviour, export an environment
variable named NERODIA_DB_PATH with
the full path towards the desired
database file location.
"""
# pylint: disable=too-few-public-methods, invalid-name

import datetime
import os

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy import ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, sessionmaker, relationship
from sqlalchemy import create_engine


NERODIA_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.abspath(os.path.join(NERODIA_DIR, os.pardir))
DEFAULT_DB_PATH = os.path.join(
    PARENT_DIR, "data", "nerodia.db"
)
DB_PATH = os.environ.get("NERODIA_DB_PATH", DEFAULT_DB_PATH)

Base = declarative_base()
Session = sessionmaker()


# pylint: disable=bad-continuation
ASSOCIATION_TABLE = Table("association", Base.metadata,
    Column('subreddit_id', Integer, ForeignKey('subreddit.id')),
    Column('stream_id', Integer, ForeignKey("stream.id"))
)

class Stream(Base):
    """
    The Stream table, used to obtain
    the ID for the given Twitch stream
    without making an API call.
    """

    __tablename__ = "stream"

    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    added_on = Column(DateTime, default=datetime.datetime.now())


class Subreddit(Base):
    """
    The Subreddit table, which
    is used to associate the
    streams being followed with
    the subreddits on which they
    are being followed.
    """

    __tablename__ = "subreddit"

    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    follows = Column(String(30), ForeignKey("stream.name"))
    streams = relationship(
        "Stream",
        secondary=ASSOCIATION_TABLE,
        backref=backref('subreddits', lazy='dynamic'),
        lazy='dynamic'
    )


engine = create_engine(f"sqlite:///{DB_PATH}")
Base.metadata.create_all(engine)
Session.configure(bind=engine)
session = Session()
