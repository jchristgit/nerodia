from abc import ABCMeta, abstractmethod


class Module(metaclass=ABCMeta):

    @property
    @abstractmethod
    def name(self):
        """Return this module's name. Must be identical to the package name."""
