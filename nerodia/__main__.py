"""
The entry point for Nerodia.
Configures logging and starts everything up.
"""


import asyncio
import importlib
import logging

from .config import CONFIG
from .pollers import stream_poller
from .twitch import TwitchClient


logging.basicConfig(
    format="%(asctime)s | %(name)38s | %(funcName)20s | %(levelname)8s | %(message)s",
    datefmt="%d.%m.%y %H:%M:%S",
    level=logging.INFO,
)

log = logging.getLogger(__name__)
logging.getLogger("discord").setLevel(logging.ERROR)


ENABLED_CONSUMERS = CONFIG["consumers"]["enabled"]
consumers = []


async def initialize_consumers(event_loop: asyncio.AbstractEventLoop, twitch_client: TwitchClient):
    for consumer_name in ENABLED_CONSUMERS:
        module = importlib.import_module(f"nerodia.consumers.{consumer_name}")
        consumer = module.Consumer(twitch_client)
        await consumer.initialize(event_loop)
        consumers.append(consumer)
        log.info(f"Initialized `{consumer_name}` consumer.")


async def cleanup_consumers():
    for consumer in consumers:
        await consumer.cleanup()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    twitch_client = TwitchClient(CONFIG["producers"]["poller"]["client-id"])

    log.info("Loading consumers...")
    loop.run_until_complete(initialize_consumers(loop, twitch_client))
    try:
        loop.run_until_complete(stream_poller(consumers, twitch_client))
    except KeyboardInterrupt:
        log.info("Got SIGINT. Shutting down...")
    loop.run_until_complete(cleanup_consumers())
    loop.close()
