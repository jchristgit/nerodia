"""
Polls the Bot's Reddit inbox for new messages.
"""

import asyncio

from .clients import reddit
from .handlers import handle_message


async def inbox_poller():
    print("[InboxPoller] Ready.")
    while True:
        for msg in reddit.inbox.unread():
            handle_message(msg)
            msg.mark_read()
        await asyncio.sleep(10)
