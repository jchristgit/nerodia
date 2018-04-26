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
from .embeds import create_stream_online_embed
from .twitch import TwitchStream
from .util import token_dict, verify_dict


log = logging.getLogger(__name__)


def verify(msg: praw.models.Message):
    """Handles a verification message received on reddit.

    This is used to connect a user's Discord account and
    their reddit account together to prove that the Discord
    user is a moderator on subreddits they want to modify.

    Args:
        msg (praw.models.Message):
            The original message.
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


def handle_message(msg: praw.models.Message):
    """Handle a new message received on reddit.

    Args:
        msg (praw.models.Message):
            The message that was received.
    """

    log.debug(
        f"Got new message from {(msg.author or msg.subreddit).name!r}, "
        f"contents: {msg.body!r}."
    )

    if msg.subject == "verification":
        verify(msg)
    elif msg.body.startswith("**gadzooks!"):
        msg.subreddit.mod.accept_invite()
        log.info(f"Accepted a Moderator invitation to {msg.subreddit.name}.")


async def handle_stream_update(
    bot: commands.Bot,
    stream_name: str,
    now_online: bool,
    stream: Optional[TwitchStream],
):
    """Handle a stream changing status.

    Args:
        bot (commands.Bot):
            The bot instance, used to notify guilds about the update.
        stream_name (str):
            The name of the stream which updated.
        now_online (bool):
            `True` if the stream is now online, `False` if it is now offline.
        stream (Optional[TwitchStream]):
            If not `None`, a `TwitchStream` instance representing the updated stream.
            If `now_online` is `True`, this is expected to not be `None`.
    """

    followers = guild_db.get_guilds_following(stream_name)

    for guild_id in followers:
        update_channel_id = guild_db.get_update_channel(guild_id)
        if update_channel_id is None:
            log.warning(
                f"Guild {guild_id} is following {stream_name!r}",
                "but has no update channel set.",
            )
        else:
            channel = bot.get_channel(update_channel_id)
            if channel is None:
                log.warning(
                    f"Guild {guild_id} has an update channel set, "
                    "but it could not be found."
                )
            elif now_online:
                embed = await create_stream_online_embed(stream_name, stream)
                await channel.send(embed=embed)
