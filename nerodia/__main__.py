"""
The entry point for Nerodia.
Starts off the Threads, one for
each class defined in workers.py.
After starting them, it sleeps
for up to one year, effectively
waiting for any signal to interrupt
it. On interruption, it puts None
onto the event queue in order for
the Reddit consumer to stop
processing input events and also
calls the `stop` method on the
other threads to make them
exit their while polling loop.
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
