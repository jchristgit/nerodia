"""
Provides handlers for the various events
that are produced by the RedditProducer.
"""

from typing import Iterable, Optional

import discord
import praw

from . import database as db
from .apis.twitch import TwitchStream
from .bot import discord_bot
from .clients import reddit
from .util import stream_states, token_dict, verify_dict


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

    print('New Message from', (msg.author or msg.subreddit).name, 'contents:', msg.body)

    if msg.subject == "verification":
        verify(msg)
    elif msg.body.startswith("**gadzooks!"):
        msg.subreddit.mod.accept_invite()
        print(f"Accepted a Moderator invitation to {msg.subreddit}.")


async def handle_stream_update(stream_name: str, is_online: bool, stream: Optional[TwitchStream]):
    """
    Handles a Stream update.
    Dispatches a sidebar update
    event for every Subreddit
    that is following the stream
    at the time the update occurs,
    as well as every discord Guild
    that is doing so.

    Arguments:
        stream_name (str):
            The stream which status changed from offline to online or the other way around.
        is_online (bool):
            Whether the given stream is now online. Used for the Discord Guild updater.
        stream (Optional[TwitchStream]):
            The TwitchStream class as returned by the API, or `None` if the stream is offline.
    """

    for sub in db.get_subreddits_following():
        notify_sub_update(stream_name)

    for guild_id in db.get_guilds_following(stream_name):
        await notify_guild_update(guild_id, stream_name, is_online, stream)


async def notify_guild_update(guild_id: int, stream_name: str, is_online: bool, stream):
    """
    Notifies a guild that is following the given
    stream about it going online or offline.

    Arguments:
        guild_id (int):
            The guild ID on which the stream update announcement channel
            should be looked up and the notice sent out.
        stream_name (str):
            The stream (name) which status has changed.
        is_online (bool):
            Whether the stream is now online or not.
        stream (Optional[TwitchStream]):
            The `TwitchStream` instance, when the stream is online.
    """

    channel_id = db.get_guild_update_channel(guild_id)

    if channel_id is None:
        channel = discord_bot.get_channel(channel_id)
        if channel is not None:
            if is_online:
                await channel.send(embed=discord.Embed(
                    title=f"{stream_name} is now online!",
                    description=f"Now playing {stream.game} for {stream.viewers} viewers:\n"
                                f"*{stream.status.strip()}*",
                    colour=0x6441A4,
                    url=f"https://twitch.tv/{stream_name}",
                ).set_image(
                    url=stream.video_banner
                ).set_thumbnail(
                    url=stream.logo
                ).set_footer(
                    text=f"Followers: {stream.followers:,} | Viewers: {stream.viewers:,}"
                ))
            else:
                await channel.send(embed=discord.Embed(
                    title=f"{stream_name} is now offline.",
                    colour=0x6441A4,
                    url=f"https://twitch.tv/{stream_name}"
                ))
        else:
            print(f"Guild {guild_id} has an update channel set, but it could not be found.")
    else:
        print(f"Guild {guild_id} has follows set, but did not set an announcement channel.")
    print(f"Updated stream {stream_name} on guild with ID {guild_id}.")


def notify_sub_update(sub: str):
    """
    Notifies the given Subreddit about an
    update on any Stream.
    This will remove the old stream
    list from its sidebar, re-build it,
    and put it where it was before.

    Arguments:
        sub (str):
            The Subreddit on which the update should be performed.
    """

    mod_relationship = reddit.subreddit(sub).mod
    current_sidebar = mod_relationship.settings()["description"]
    stream_start_idx = find_stream_start_idx(current_sidebar)
    if stream_start_idx is None:
        print(sub, "is following streams, but no header was found.")
    else:
        clean_sidebar = remove_old_stream_list(current_sidebar)
        sidebar_with_streams = add_stream_list(
            clean_sidebar,
            stream_start_idx,
            (stream for stream in db.get_subreddit_follows(sub) if stream_states[stream])
        )
        mod_relationship.update(description=sidebar_with_streams)


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


def add_stream_list(sidebar: str, start_idx: int, streams: Iterable[str]) -> str:
    """
    Adds the stream list to the Subreddit.
    Make sure to remove the old streams list
    beforehand using `remove_old_stream_list`
    to ensure that no duplicate entries will
    be on the list.

    Streams are added into the following format:
        # Streams
        > stream_name
        > another_stream
        > more_streams
    The lines containing stream names end with
    two spaces to ensure that the formatting
    will not put them together onto a single line.

    Arguments:
        sidebar (str):
            The sidebar to which the streams list should be added.
            The original argument is not modified.
        start_idx (int):
            The index of the last character of the header, which
            is usually `s` (from `# Streams`).
            Can be obtained by using `find_stream_start_idx`.
        streams (Iterable[str]):
            An iterable of strings containing the names of the
            streams which should be put onto the subreddit's
            sidebar below the streams header.
            Can be a list, but it is recommended to use a
            generator (expression) for efficiency.

    Returns:
        str:
            The updated sidebar, containing a list of streams
            in quotes (prefixed with `> ` and with two spaces
            appended). Aside from adding the list of streams,
            this does not differ from the original sidebar.
    """

    # See format description above.
    streams_as_string = "\n> " + "  \n> ".join(streams) + "  \n"

    return sidebar[:start_idx + 1] + streams_as_string + sidebar[start_idx + 1:]
