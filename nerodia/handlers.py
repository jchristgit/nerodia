"""
Provides handlers for events,
for example responding to
reddit messages,  verifying
a user, or updating a Discord
server about a stream update.
"""

import logging
from typing import Optional

from discord.ext import commands

from .consumers.discordbot.embeds import create_stream_online_embed
from .database import guilds as guild_db
from .twitch import TwitchStream


log = logging.getLogger(__name__)


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
