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
    def __init__(self):
        super().__init__(daemon=True)
        self.should_stop = False

    def stop(self):
        self.should_stop = True


class RedditConsumer(StoppableThread):
    def run(self):
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
    def run(self):
        print("[RedditProducer] Ready.")
        while not self.should_stop:
            for msg in reddit.inbox.unread():
                event_queue.put(('msg', msg))
                msg.mark_read()
            time.sleep(10)


class TwitchProducer(StoppableThread):
    def run(self):
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
