"""
Provides handlers for the various events
that are produced by the RedditProducer.
"""

from typing import Tuple

import praw

from .util import token_dict, token_lock, verify_dict, verify_lock


def _get_stream_name(full_msg: praw.models.Message) -> str:
    return ' '.join(full_msg.body.split()[1:])


def handle_verify(msg: praw.models.Message):
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
        msg.reply("You have connected your accounts successfully!")
    else:
        msg.reply(f"> {msg.body}\n\nFailed to connect accounts: Unknown token.")


def handle_message(event: Tuple[str, praw.models.Message]) -> None:
    """
    Handles the message Event and processes the new message.
    """

    _, msg = event
    print('New Message from', msg.author.name, 'contents:', msg.body)

    if msg.subject == "verification":
        print("wants to verify.")
        handle_verify(msg)
