"""
The entry point for Nerodia.
Configures logging and starts everything up.
"""


import asyncio
import logging

from .config import CONFIG
from .core import Nerodia
from .pollers import stream_poller
from .twitch import TwitchClient


logging.basicConfig(
    format="%(asctime)s | %(name)38s | %(funcName)20s | %(levelname)8s | %(message)s",
    datefmt="%d.%m.%y %H:%M:%S",
    level=logging.INFO,
)

log = logging.getLogger(__name__)
logging.getLogger("discord").setLevel(logging.ERROR)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    nerodia = Nerodia(CONFIG, loop)
    twitch_client = TwitchClient(CONFIG["producers"]["poller"]["client-id"])

    nerodia.run(twitch_client, stream_poller)
    loop.close()
