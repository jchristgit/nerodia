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

import os

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy import ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
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
    Column('followed_by', String(30), ForeignKey('subreddits.follows')),
    Column('follows', String(30), ForeignKey("streams.name"))
)

class Stream(Base):
    """
    The Stream table, used to obtain
    the ID for the given Twitch stream
    without making an API call.
    """

    __tablename__ = "streams"

    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    added_on = Column(DateTime)
    followed_by = relationship(
        "Subreddit",
        secondary=ASSOCIATION_TABLE,
        back_populates="all_follows"
    )


class Subreddit(Base):
    """
    The Subreddit table, which
    is used to associate the
    streams being followed with
    the subreddits on which they
    are being followed.
    """

    __tablename__ = "subreddits"

    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    follows = Column(String(30), ForeignKey("streams.name"))
    all_follows = relationship(
        "Stream",
        secondary=ASSOCIATION_TABLE,
        back_populates="followed_by"
    )


engine = create_engine(f"sqlite:///{DB_PATH}")
Base.metadata.create_all(engine)
Session.configure(bind=engine)
session = Session()
