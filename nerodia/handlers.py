"""
Provides handlers for events,
for example responding to
reddit messages,  verifying
a user, or updating a Discord
server about a stream update.
"""

import logging
from typing import Optional

import praw
from discord.ext import commands

from .database import guilds as guild_db
from .twitch import TwitchStream
from .util import token_dict, verify_dict


log = logging.getLogger(__name__)


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

    log.debug(
        f"Got new message from {(msg.author or msg.subreddit).name!r}, contents: {msg.body!r}."
    )

    if msg.subject == "verification":
        verify(msg)
    elif msg.body.startswith("**gadzooks!"):
        msg.subreddit.mod.accept_invite()
        log.info(f"Accepted a Moderator invitation to {msg.subreddit.name}.")


async def handle_stream_update(bot: commands.Bot, stream_name: str, now_online: bool, stream: Optional[TwitchStream]):
    followers = guild_db.get_guilds_following(stream_name)

    for guild_id in followers:
        update_channel_id = guild_db.get_update_channel(guild_id)
        if update_channel_id is None:
            log.warn(f"Guild {guild_id} is following {stream_name!r}, but has no update channel set.")
        else:
            channel = await discord_bot.get_channel(update_channel_id)
            if channel is None:
                log.warn(f"Guild {guild_id} has an update channel set, but it could not be found.")
            else:
                await channel.send(f"**{stream_name}** is now {'online' if now_online else 'offline'}!")
