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
    followed_now = ', '.join(storage.all_follows()) or 'No Streams are being followed :('
    print('New Message from', msg.author.name, 'contents:', msg.body)

    if msg.body.startswith("follow"):
        stream_name = _get_stream_name(msg)
        if not stream_name:
            msg.reply(BOT_USAGE_INFO)
        elif not storage.stream_exists(stream_name):
            msg.reply(f"**Failed to follow {stream_name}**: Couldn't find the Stream. Are you sure it exists?")
        elif stream_name in storage.all_follows():
            msg.reply(f"I'm already following {stream_name}. :(")
        else:
            storage.follow_stream(stream_name)
            msg.reply(
                f"**Followed {stream_name}!**\n\nThe following Streams are now being followed:\n{followed_now}"
            )

    elif msg.body.startswith("unfollow"):
        stream_name = _get_stream_name(msg)
        if not stream_name:
            msg.reply(BOT_USAGE_INFO)
        elif stream_name not in storage.all_follows():
            msg.reply(
                f"The stream {stream_name} wasn't followed - these are the ones I'm following:\n\n{followed_now}"
            )
        else:
            storage.unfollow_stream(stream_name)
            msg.reply(
                f"**I unfollowed the stream {stream_name}.**\n\nThese are my updated follows:\n{followed_now}"
            )

    elif msg.body == "follows":
        msg.reply('# All follows:\n' + ', '.join(storage.all_follows()))

    elif msg.body == 'help':
        msg.reply(BOT_USAGE_INFO)
