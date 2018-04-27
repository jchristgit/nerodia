import asyncio
from abc import ABCMeta, abstractmethod

from nerodia.twitch import TwitchStream, TwitchUser


class Consumer(metaclass=ABCMeta):
    """The base class for all consumers.

    Defines a common interface that all consumers must implement.
    This is used once an update is received by the producers.
    """

    @abstractmethod
    async def initialize(self, loop: asyncio.AbstractEventLoop):
        """Run any code that is required to run before the polling starts."""

    @abstractmethod
    async def cleanup(self):
        """Run any code that is required to run before nerodia exits."""

    @abstractmethod
    async def stream_online(self, stream: TwitchStream, user: TwitchUser):
        """Called when the given `stream` changes state to online."""

    @abstractmethod
    async def stream_offline(self, user: TwitchUser):
        """Called when the given `user`'s stream goes offline."""
