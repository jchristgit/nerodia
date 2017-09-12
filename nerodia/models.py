"""
Database file. Contains the table
classes and relationships for
the Subreddit as well as the Stream
tables. Each subreddit can follow
0 - n streams, and each stream can
be followed by 0 - n subreddits, thus
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

from sqlalchemy import BigInteger, Column, DateTime, Integer, String
from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


NERODIA_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.abspath(os.path.join(NERODIA_DIR, os.pardir))
DEFAULT_DB_PATH = os.path.join(
    PARENT_DIR, "data", "nerodia.db"
)
DB_PATH = os.environ.get("NERODIA_DB_PATH", DEFAULT_DB_PATH)

Base = declarative_base()
Session = sessionmaker()


class Stream(Base):
    """
    The Stream table, used to obtain
    the ID for the given Twitch stream
    without making an API call.
    """

    __tablename__ = "stream"

    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    stream_id = Column(Integer, nullable=False)
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
    name = Column(String(30), nullable=False)
    follows = Column(String(30), ForeignKey("stream.name"))


class Guild(Base):
    """
    The Guild table, which
    represents a Discord guild
    following a stream. A single
    Discord guild can follow 0-n
    Streams, and will receive
    updates for it in a channel
    set through the Discord bot.
    """

    __tablename__ = "guild"

    discord_id = Column(BigInteger, primary_key=True)
    follows = Column(String(30), ForeignKey("stream.name"))


class UpdateChannel(Base):
    """
    The UpdateChannel table, which
    contains the Guild Discord ID
    and its associated channel ID
    in which stream updates are
    posted. This can be set through
    the Discord Bot interface.
    """

    __tablename__ = "updatechannel"

    channel_id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey("guild.discord_id"))


class DRConnection(Base):
    """
    The Discord ID <-> Reddit table.
    Contains Discord IDs associated
    with a reddit name. Discord users
    agree to this in the
    "connectreddit" command.
    """

    __tablename__ = "drmapping"

    discord_id = Column(BigInteger, primary_key=True)
    reddit_name = Column(String(30), nullable=False)


engine = create_engine(f"sqlite:///{DB_PATH}")
Base.metadata.create_all(engine)
Session.configure(bind=engine)
session = Session()
