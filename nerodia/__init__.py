# flake8: noqa

try:
    import uvloop
except ImportError:
    pass
else:
    import asyncio
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

from . import (
    database,
    bot, cog, clients, handlers,
    util, workers
)

__all__ = [
    "database",
    "bot", "cog", "clients", "handlers",
    "util", "workers"
]
