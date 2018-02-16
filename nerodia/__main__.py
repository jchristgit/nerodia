"""
The entry point for Nerodia.
"""


import asyncio

from .bot import discord_bot
from .config import DISCORD_CFG
from .clients import twitch
from .workers import inbox_poller


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    poller = loop.create_task(inbox_poller())

    try:
        loop.run_until_complete(discord_bot.start(DISCORD_CFG['token']))
    except KeyboardInterrupt:
        poller.cancel()
        loop.run_until_complete(discord_bot.logout())
    finally:
        loop.close()
