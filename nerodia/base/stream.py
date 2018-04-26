from abc import ABCMeta, abstractmethod


class Stream(metaclass=ABCMeta):
    """Contains information about a stream."""

    @property
    @abstractmethod
    def id(self) -> int:
        """Holds the ID of this `Stream`."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Holds the name of this `Stream`."""
