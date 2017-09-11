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

from .bot import NerodiaDiscordBot
from .clients import discord_game, discord_token
from .workers import reddit_consumer, reddit_producer, twitch_producer


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    rc = loop.create_task(reddit_consumer())
    rp = loop.create_task(reddit_producer())
    tp = loop.create_task(twitch_producer())

    bot = NerodiaDiscordBot(discord_game)
    try:
        loop.run_until_complete(bot.start(discord_token))
    except KeyboardInterrupt:
        print("Stopping the workers...")
        tp.cancel()
        rp.cancel()
        rc.cancel()
        print("Workers stopped. Logging out the Discord Bot...")
        loop.run_until_complete(bot.logout())
        print("Bot logged out.")
    finally:
        loop.close()
