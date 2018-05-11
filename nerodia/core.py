import asyncio
import logging
import importlib


log = logging.getLogger(__name__)


class Nerodia:

    def __init__(self, config, loop: asyncio.AbstractEventLoop):
        self.config = config
        self.consumers = set()
        self.loop = loop
        self.modules = set()

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
        consumer = module.Consumer(twitch_client, self)

        if consumer in self.consumers:
            log.error(
                f"Attempted to load consumer {consumer_name}, but it already is loaded!"
            )
            raise ValueError(f"Consumer {consumer_name} is already loaded.")

        await consumer.initialize(self.loop)
        log.info(f"Initialized consumer `{consumer.__class__.__name__}`.")

        self.consumers.add(consumer)

    async def load_module(self, module_path: str):
        if "." in module_path:
            consumer_for_module = module_path.split(".")[0]
            consumer = next(
                (c for c in self.consumers if c.name == consumer_for_module), None
            )

            if consumer is None:
                error_text = (
                    f"Tried loading module {module_path} for consumer "
                    f"{consumer_for_module}, but the consumer could not be found."
                )
                log.error(error_text)
                raise ValueError(error_text)

            module = importlib.import_module(f"nerodia.modules.{module_path}")
            module_instance = module.Module(self)
            await consumer.load_module(module_instance)
            self.modules.add(module_instance)

        else:
            raise NotImplementedError(
                "Application-level modules are not supported yet."
            )
            # module = importlib.import_module(f"nerodia.modules.nerodia.{module_path}")

    async def unload_module(self, module_path: str, remove_from_set: bool = True):
        if "." in module_path:
            consumer_for_module = module_path.split(".")[0]
            consumer = next(
                (c for c in self.consumers if c.name == consumer_for_module), None
            )

            if consumer is None:
                error_text = (
                    f"Tried unloading module {module_path} for consumer "
                    f"{consumer_for_module}, but the consumer could not be found."
                )
                log.error(error_text)
                raise ValueError(error_text)

            module = next((m for m in self.modules if m.name == module_path), None)
            if module is None:
                error_text = f"Cannot unload already unloaded module {module_path}."
                log.error(error_text)
                raise ValueError(error_text)

            await consumer.unload_module(module_path)
            if remove_from_set:
                self.modules.remove(module)

        else:
            raise NotImplementedError(
                "Application-level modules are not supported yet."
            )

    def run(self, twitch_client, stream_poller):
        enabled_consumers = self.config["consumers"]["enabled"]
        enabled_modules = self.config["modules"]["enabled"]

        log.info("Loading consumers...")
        for consumer in enabled_consumers:
            self.loop.run_until_complete(
                self.initialize_consumer(twitch_client, consumer)
            )

        log.info("Loading modules...")
        for module_path in enabled_modules:
            self.loop.run_until_complete(self.load_module(module_path))

        try:
            self.loop.run_until_complete(stream_poller(self.consumers, twitch_client))
        except KeyboardInterrupt:
            log.info("Got SIGINT. Shutting down...")

        for module in self.modules:
            self.loop.run_until_complete(self.unload_module(module.name, remove_from_set=False))

        self.modules.clear()
        self.loop.run_until_complete(self.cleanup_all_consumers())
