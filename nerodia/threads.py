"""
Contains the threads as defined in
`workers.py` as well as various
utility functions to control the
threads, get information about their
status, and more.
"""

from .workers import event_queue, RedditConsumer, RedditProducer, TwitchProducer

THREADS = (
    RedditConsumer(),
    RedditProducer(),
    TwitchProducer()
)


def start_all():
    """
    Starts all threads.
    """

    for t in THREADS:
        t.start()


def shutdown_all():
    """
    Sets the `should_stop` attribute
    on all threads through the `.stop`
    method and joins them with the
    main thread afterwards. Additionally,
    passes `None` into the event queue,
    as the `RedditConsumer` thread
    blocks on the queue until a signal
    arrives. This allows it to shutdown
    almost instantly, compared to the
    other threads which usually require
    multiple seconds to shut down.
    """

    event_queue.put(None)
    for t in THREADS:
        t.stop()

    for t in THREADS:
        t.join()
