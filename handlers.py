from typing import Any, Tuple

import praw

import storage


BOT_USAGE_INFO = """
# Bot Usage
The following commands are available:

- `follow <stream_name>` Follows the given Stream.
- `unfollow <stream_name>` Unfollows the given Stream.
- `follows` Sends a list of all followed Streams.
- `help` Sends this.

In addition to the `follows` command, the commands `follow` and `unfollow`
also show the resulting follows after the command was used.
"""


def _get_stream_name(full_msg: praw.models.Message) -> str:
    return ' '.join(full_msg.body.split()[1:])


def handle_message(event: Tuple[str, praw.models.Message]) -> None:
    msg = event[1]

    if msg.body.startswith("follow"):
        stream_name = _get_stream_name(msg)
        if not stream_name:
            msg.reply(BOT_USAGE_INFO)
        storage.follow_stream(stream_name)

    elif msg.body.startswith("unfollow"):
        stream_name = _get_stream_name(msg)
        if not stream_name:
            msg.reply(BOT_USAGE_INFO)

    elif msg.body == "follows":
        msg.reply(
            '# All follows:\n' + ', '.join(storage.all_follows())
        )
