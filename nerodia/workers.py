"""
Contains the class definitions
for various workers that are
used by Nerodia, namely:

- The Reddit Consumer, which
waits for events in a queue
and passes them to their
designated handlers.

- The Reddit Producer, which
polls for reddit direct messages
in a set interval and puts them
into the event queue when necessary.

- The Twitch Producer, which polls
the Twtch API for stream updates.
Puts events for the stream going
online / offline into the event
queue when states change.
"""

import asyncio

from . import database as db
from .clients import reddit, twitch
from .handlers import handle_message, handle_stream_update
from .util import stream_states

# Events get returned in tuples indicating what is supposed to be done and data about it.
# The following events are implemented:
# ('on', <stream_name>) - stream status update. stream went online
# ('off', <stream_name>) - stream status update. stream went offline
# ('msg', <message_instance>) - sent when a message is received from an authorized user.
event_queue = asyncio.Queue()

loop = asyncio.get_event_loop()


async def reddit_consumer():
    print("[RedditConsumer] Ready.")
    try:
        while True:
            event = await event_queue.get()

            if event[0] == 'on':
                await handle_stream_update(event[1].name, is_online=True, stream=event[1])
            elif event[0] == 'off':
                await handle_stream_update(event[1], is_online=False, stream=None)
            elif event[0] == 'msg':
                handle_message(event[1])
            else:
                print("[RedditConsumer]: Unknown Event:", event)

            event_queue.task_done()

    except asyncio.CancelledError:
        print("[RedditConsumer] Cancelled.")


async def reddit_producer():
    print("[RedditProducer] Ready.")
    try:
        while True:
            for msg in reddit.inbox.unread():
                print("[RedditProducer] Got a message from", msg.author)
                await event_queue.put(('msg', msg))
                msg.mark_read()
            await asyncio.sleep(10)

    except asyncio.CancelledError:
        print("[RedditProducer] Cancelled.")


async def twitch_producer():
    print("[TwitchProducer] Ready.")
    try:
        while True:
            follows = db.get_all_follows()
            for stream_name in follows:
                stream_id = await db.get_stream_id(stream_name)
                stream = await twitch.get_stream_by_user_id(stream_id)
                stream_is_online = stream is not None

                if stream_states.get(stream_name, stream_is_online) != stream_is_online:
                    if stream_is_online:
                        await event_queue.put(('on', stream))
                    else:
                        await event_queue.put(('off', stream_name))

                stream_states[stream_name] = stream_is_online
                await asyncio.sleep(1)

            await asyncio.sleep(10)

    except asyncio.CancelledError:
        print("[TwitchProducer] Cancelled.")
