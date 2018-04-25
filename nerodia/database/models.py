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

import pathlib
import os

from sqlalchemy import BigInteger, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


CWD = pathlib.Path.cwd()
DEFAULT_DB_PATH = CWD / "data" / "nerodia.db"
DB_PATH = os.environ.get("NERODIA_DB_PATH", DEFAULT_DB_PATH)

Base = declarative_base()
Session = sessionmaker()


class Follow(Base):
    """
    The follow table, which
    associates either a Discord
    Guild ID or a subreddit name
    with a stream name that it
    is following.
    """

    __tablename__ = "follow"

    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger)
    sub_name = Column(String(30))
    follows = Column(String(30), nullable=False)

    def __init__(self, follows: str, *, guild_id: int = None, sub_name: str = None):
        self.follows = follows
        self.guild_id = guild_id
        self.sub_name = sub_name


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

    guild_id = Column(BigInteger, primary_key=True)
    channel_id = Column(BigInteger, primary_key=True)


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
    reddit_name = Column(String(30), primary_key=True)


class SidebarTemplate(Base):
    """
    Contains the Subreddit sidebar template
    which will be used for updating it with
    a list of online streams.
    """

    __tablename__ = "sidebartemplate"

    subreddit = Column(String(30), primary_key=True)
    template = Column(String(10_240), nullable=False)


engine = create_engine(f"sqlite:///{DB_PATH}")
Session.configure(bind=engine)
session = Session()
