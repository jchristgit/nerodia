import threading
import time
import json

import praw

from queue import Queue

from event_handlers import handle_message

# Events get returned in tuples indicating what is supposed to be done and data about it.
# The following events are implemented:
# ('online', <stream_name>) - sent whenever a Twitch Stream goes online.
# ('offline', <stream_name>) - sent whenever a Twitch Stream goes offline.
# ('msg', <message_contents>) - sent when a message is received from an authorized user.
event_queue = Queue()

with open("config.json", 'r') as f:
    _auth_data = json.load(f)["reddit_auth"]

reddit = praw.Reddit(
    client_id=_auth_data["client_id"],
    client_secret=_auth_data["client_secret"],
    username=_auth_data["username"],
    password=_auth_data["password"],
    user_agent=_auth_data["user_agent"]
)


class StoppableThread(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.should_stop = False

    def stop(self):
        self.should_stop = True


class RedditConsumer(StoppableThread):
    def run(self):
        print('Polling for Reddit Events (consumer)')
        while not self.should_stop:
            event = event_queue.get()

            # Program wants to terminate, stop the thread
            if event is None:
                return
            elif event[0] == 'online':
                pass
            elif event[0] == 'offline':
                pass
            else:
                handle_message(event)
            time.sleep(2)


class RedditProducer(StoppableThread):
    def run(self):
        while not self.should_stop:
            time.sleep(2)
            print('redditp')


class TwitchProducer(StoppableThread):
    def run(self):
        while not self.should_stop:
            time.sleep(1)
            print('twitchp')

