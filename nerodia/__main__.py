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

import time

from . import workers
from .bot import NerodiaDiscordBot
from .clients import discord_token

SECONDS_IN_A_YEAR = 60 * 60 * 24 * 365

if __name__ == '__main__':
    THREADS = [
        workers.RedditConsumer(),
        workers.RedditProducer(),
        workers.TwitchProducer()
    ]

    for t in THREADS:
        t.start()

    discord_bot = NerodiaDiscordBot(discord_token)
    discord_bot.run()
    print("Stopped the Discord Bot. Hit ^C again to stop the Workers.")

    try:
        time.sleep(SECONDS_IN_A_YEAR)
    except KeyboardInterrupt:
        pass
    finally:
        print("Stopping Workers...")
        workers.event_queue.put(None)

        for t in THREADS:
            t.stop()
        for t in THREADS:
            t.join()
