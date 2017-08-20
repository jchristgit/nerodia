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

from . import workers
from .bot import NerodiaDiscordBot
from .clients import discord_token

if __name__ == '__main__':
    THREADS = (
        workers.RedditConsumer(),
        workers.RedditProducer(),
        workers.TwitchProducer()
    )

    for t in THREADS:
        t.start()

    NerodiaDiscordBot(discord_token).run()
    print("Stopped the Discord Bot. Stopping the Workers...")

    workers.event_queue.put(None)

    for t in THREADS:
        t.stop()
    for t in THREADS:
        t.join()
