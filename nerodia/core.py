import asyncio
import logging
import importlib


log = logging.getLogger(__name__)


class Nerodia:

    def __init__(self, config, loop: asyncio.AbstractEventLoop):
        self.config = config
        self.consumers = set()
        self.loop = loop

    async def cleanup_consumer(self, consumer_name: str):
        """Cleans up the specified consumer and removes it from nerodia."""

        consumer = next((c for c in self.consumers if c.name == consumer_name), None)
        if consumer is None:
            log.error(
                f"Tried to clean up consumer {consumer_name}, "
                "but it could not be found."
            )
            raise ValueError(f"Unknown consumer: {consumer_name}")

        await consumer.cleanup()
        self.consumers.remove(consumer)
        log.info(f"Cleaned up consumer `{consumer.__class__.__name__}`.")

    async def cleanup_all_consumers(self):
        """Clean up any running consumers, and remove them from nerodia."""

        for consumer in self.consumers:
            await consumer.cleanup()
            log.info(f"Cleaned up consumer `{consumer.__class__.__name__}`.")

        # Clean the internal consumer set
        self.consumers = set()

    async def initialize_consumer(self, twitch_client, consumer_name: str):
        """Import, initialize and add consumer to nerodia."""

        module = importlib.import_module(f"nerodia.consumers.{consumer_name}")
        consumer = module.Consumer(twitch_client)

        if consumer in self.consumers:
            log.error(
                f"Attempted to load consumer {consumer_name}, but it already is loaded!"
            )
            raise ValueError(f"Consumer {consumer_name} is already loaded.")

        await consumer.initialize(self.loop)
        log.info(f"Initialized consumer `{consumer.__class__.__name__}`.")

        self.consumers.add(consumer)

    def run(self, twitch_client, stream_poller):
        log.info("Loading consumers...")
        enabled_consumers = self.config["consumers"]["enabled"]

        for consumer in enabled_consumers:
            self.loop.run_until_complete(
                self.initialize_consumer(twitch_client, consumer)
            )

        try:
            self.loop.run_until_complete(stream_poller(self.consumers, twitch_client))
        except KeyboardInterrupt:
            log.info("Got SIGINT. Shutting down...")

        self.loop.run_until_complete(self.cleanup_all_consumers())
