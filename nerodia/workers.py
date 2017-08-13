"""
Contains the class definitions
for various workers that are
used by Nerodia, namely:

- The Reddit Consumer, which
waits for events in a queue
and passes them to their
designated handlers

- The Reddit Producer, which
polls for reddit direct messages
in a set interval and puts them
into the event queue when necessary.

- The Twitch Producer, which polls
the Twtch API for stream updates.
Puts events for the stream going
online / offline into the event
queue when states change.

This also defines a class called
`StoppableThread` which adds a
simple variable to a
`threading.Thread` which it uses
in its main loop to check whether
it should stop or keep running.
"""

import threading
import time
from queue import Queue

from . import poller
from . import storage
from .clients import reddit
from .handlers import handle_message

# Events get returned in tuples indicating what is supposed to be done and data about it.
# The following events are implemented:
# ('on', <stream_name>) - sent whenever a Twitch Stream goes on.
# ('off', <stream_name>) - sent whenever a Twitch Stream goes offline.
# ('msg', <message_instance>) - sent when a message is received from an authorized user.
event_queue = Queue()


class StoppableThread(threading.Thread):
    """
    A subclass of `threading.Thread`
    which has an additional attribute
    called `should_stop` which should
    be used as a stopping condition
    inside a thread's `run` method in
    order for this to be effective,
    for example in a while loop.
    """

    def __init__(self):
        super().__init__(daemon=True)
        self.should_stop = False

    def stop(self):
        self.should_stop = True


class RedditConsumer(StoppableThread):
    """
    The reddit consumer thread.
    Waits for new events to appear in
    the the event queue, then dispatches
    it to different event handlers as
    necessary, or stops on the event `None`.
    """

    def run(self):
        """
        Start the RedditConsumer thread.
        Does not sleep for any time between
        runs, since it just blocks until a
        new event is received, and the event
        `None` is dispatched when the thread
        should stop.
        """

        print('[RedditConsumer] Ready.')
        while not self.should_stop:
            event = event_queue.get()

            # Program wants to terminate, stop the thread
            if event is None:
                return
            elif event[0] == 'on':
                print('Now online:', event[1])
            elif event[0] == 'off':
                print('Now offline:', event[1])
            else:
                handle_message(event)

            event_queue.task_done()


class RedditProducer(StoppableThread):
    """
    The reddit producer thread.
    Polls for new direct messages
    in a set interval, and adds
    them to the event queue as they
    come in, so that no polling is
    performed in the reddit
    consumer thread.
    """

    def run(self):
        """
        Start the reddit producer thread.
        This sleeps for 10 seconds between
        inbox polls, but does not perform
        any message handling - instead, the
        event is dispatched into the queue
        so that the RedditProducer can
        handle it accordingly.
        """

        print("[RedditProducer] Ready.")
        while not self.should_stop:
            for msg in reddit.inbox.unread():
                event_queue.put(('msg', msg))
                msg.mark_read()
            time.sleep(10)


class TwitchProducer(StoppableThread):
    """
    The Twitch producer thread.
    Waits for Twitch streams
    to change their state - previous
    states are saved - and puts events
    indicating them going online or
    offline into the event queue when
    necessary.
    """

    def run(self):
        """
        Start the Twitch producer thread.
        Since it sleeps for 10 seconds between
        polling runs, and for one second between
        streams, stopping this thread might take
        a bit longer than the other threads.
        """

        print("[TwitchProducer] Ready.")
        stream_states = {}
        while not self.should_stop:
            for stream_name in storage.all_follows():
                stream_is_online: bool = poller.is_online(stream_name)
                # Compare the Stream state to the last one known, ignore it if it wasn't found.
                if stream_states.get(stream_name, stream_is_online) != stream_is_online:
                    event_queue.put(
                        ('on' if stream_is_online else 'off', stream_name)
                    )
                stream_states[stream_name] = stream_is_online
                time.sleep(1)

            time.sleep(10)
