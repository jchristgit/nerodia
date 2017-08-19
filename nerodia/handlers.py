"""
Provides handlers for the various events
that are produced by the RedditProducer.
"""

from typing import Optional, Tuple

import praw

from . import database as db
from .clients import reddit
from .util import reddit_lock, token_dict, token_lock, verify_dict, verify_lock


def verify(msg: praw.models.Message):
    """
    Handles a message with the subject `verify`,
    which was usually sent by a Discord user in
    order to connect his reddit account to his
    Discord account for easy usage of other commands.
    """

    with token_lock:
        for key, val in token_dict.items():
            if msg.body == val:
                discord_id = key
                break
        else:
            discord_id = None

    if discord_id is not None:
        with verify_lock:
            verify_dict[discord_id] = msg.author.name
        with reddit_lock:
            msg.reply("You have connected your accounts successfully!")
    else:
        with reddit_lock:
            msg.reply(f"> {msg.body}\n\nFailed to connect accounts: Unknown token.")


def handle_message(event: Tuple[str, praw.models.Message]) -> None:
    """
    Handles the message Event and processes the new message.
    """

    _, msg = event
    print('New Message from', (msg.author or msg.subreddit).name, 'contents:', msg.body)

    if msg.subject == "verification":
        verify(msg)
    elif msg.body.startswith("**gadzooks!"):
        with reddit_lock:
            msg.subreddit.mod.accept_invite()
        print(f"Accepted a Moderator invitation to {msg.subreddit}.")


def handle_stream_update(stream_name: str):
    """
    Handles a Stream update.
    Dispatches a sidebar update
    event for every Subreddit
    that is following the stream
    at the time the update occurs.

    Arguments:
        stream_name (str):
            The stream which status changed from offline to online or the other way around.
    """

    following_subreddits = db.get_subreddits_following(stream_name)
    print("stream status update on", stream_name)
    print("Following:", following_subreddits)

    for sub in following_subreddits:
        notify_update(sub, stream_name)


def notify_update(sub: str, stream: str):
    """
    Notifies the given Subreddit about an
    update on the given Stream. Usually,
    this will just remove the old stream
    list from its sidebar, re-build it,
    and put it where it was before.

    Arguments:
        sub (str):
            The Subreddit on which the update should be performed.
        stream (str):
            The stream which state has changed.
    """

    with reddit_lock:
        current_sidebar = reddit.subreddit(sub).mod.settings()["description"]
    stream_start_idx = find_stream_start_idx(current_sidebar)
    remove_old_stream_list(current_sidebar, stream_start_idx)


def find_stream_start_idx(sidebar: str) -> Optional[int]:
    """
    Attempts to find the character `s` of the
        "# Streams"
    header and returns the index of it.
    In the future, this could be improved by
    allowing subreddits to set a "stream-list-marker"
    for each subreddit and thus being able
    to further customize where the stream
    ilst gets written by the bot.

    Arguments:
        sidebar (str):
            The subreddit sidebar to search.

    Returns:
        Optional[int]:
            The index of character "s" of the `# Streams`
            header, or `None` if it could not be found.
    """

    index = sidebar.find("# Streams")
    if index == -1:
        return None
    return index + len("# Streams") - 1


def remove_old_stream_list(sidebar: str) -> str:
    """
    Removes the old stream list of a Subreddit,

    Arguments:
        sidebar (str): The current sidebar of the Subreddit.

    Returns:
        str: The sidebar without the old streams.
    """

    as_list = sidebar.splitlines()
    updated = as_list.copy()
    previous_line = ""

    for line in as_list:
        if previous_line == "# Streams" or previous_line.startswith(">"):
            if line.startswith(">"):
                updated.remove(line)
        previous_line = line

    return '\n'.join(updated)
