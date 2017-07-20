from threading import Thread
import time

import workers


if __name__ == '__main__':
    threads = [
        workers.RedditConsumer(),
        workers.RedditProducer(),
        workers.TwitchProducer()
    ]

    for t in threads:
        t.start()

    time.sleep(6)
    print('Stopping threads')
    workers.event_queue.put(None)
    for t in threads:
        t.stop()
        t.join()

