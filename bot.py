import workers


if __name__ == '__main__':
    threads = [
        workers.RedditConsumer(),
        workers.RedditProducer(),
        workers.TwitchProducer()
    ]

    for t in threads:
        t.start()

    try:
        input("Press any key to stop...")
    except KeyboardInterrupt:
        pass
    finally:
        print("Stopping Workers...")
        workers.event_queue.put(None)
        for t in threads:
            t.stop()
            t.join()

