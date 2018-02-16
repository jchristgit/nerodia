"""
Provides handlers for the various events
that are produced by the RedditProducer.
"""

import praw

from .util import token_dict, verify_dict


def verify(msg: praw.models.Message):
    """
    Handles a message with the subject `verify`,
    which was usually sent by a Discord user in
    order to connect his reddit account to his
    Discord account for easy usage of other commands.
    """

    for key, val in token_dict.items():
        if msg.body == val:
            discord_id = key
            break
    else:
        discord_id = None

    if discord_id is not None:
        verify_dict[discord_id] = msg.author.name
        msg.reply("You have connected your accounts successfully!")
    else:
        msg.reply(f"> {msg.body}\n\nFailed to connect accounts: Unknown token.")


def handle_message(msg: praw.models.Message) -> None:
    """
    Handles the message Event and processes the new message.
    """

    print('New Message from', (msg.author or msg.subreddit).name, 'content:', msg.body)

    if msg.subject == "verification":
        verify(msg)
    elif msg.body.startswith("**gadzooks!"):
        msg.subreddit.mod.accept_invite()
        print(f"Accepted a Moderator invitation to {msg.subreddit}.")
