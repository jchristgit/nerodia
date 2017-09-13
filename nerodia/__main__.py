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
from .clients import discord_token, twitch
from .workers import reddit_consumer, reddit_producer, twitch_producer


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    rc = loop.create_task(reddit_consumer())
    rp = loop.create_task(reddit_producer())
    tp = loop.create_task(twitch_producer())

    try:
        loop.run_until_complete(discord_bot.start(discord_token))
    except KeyboardInterrupt:
        tp.cancel()
        twitch.close()

        rp.cancel()
        rc.cancel()

        loop.run_until_complete(discord_bot.logout())
    finally:
        loop.close()
