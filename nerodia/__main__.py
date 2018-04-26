"""
The entry point for Nerodia.
Configures logging and starts the bot.
"""


import asyncio
import importlib
import logging

from .config import CONFIG


logging.basicConfig(
    format="%(asctime)s | %(name)35s | %(funcName)15s | %(levelname)8s | %(message)s",
    datefmt="%d.%m.%y %H:%M:%S",
    level=logging.INFO,
)

log = logging.getLogger(__name__)
logging.getLogger("discord").setLevel(logging.ERROR)


ENABLED_CONSUMERS = CONFIG["consumers"]["enabled"]
consumers = []


async def initialize_consumers(event_loop: asyncio.AbstractEventLoop):
    for consumer_name in ENABLED_CONSUMERS:
        module = importlib.import_module(f"nerodia.consumers.{consumer_name}")
        consumer = module.Consumer()
        await consumer.initialize(event_loop)
        consumers.append(consumer)


async def cleanup_consumers():
    for consumer in consumers:
        await consumer.cleanup()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    loop.run_until_complete(initialize_consumers(loop))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        log.info("Got SIGINT. Shutting down...")
    loop.run_until_complete(cleanup_consumers())
    loop.close()
