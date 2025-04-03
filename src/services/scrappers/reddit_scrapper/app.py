import sys

from src.collectors.reddit_collector import RedditDataCollector
from src.queue.redis_queue_manager import RedisQueueManager



if __name__ == "__main__":
    try:
        reddit_instance = RedditDataCollector(
            RedisQueueManager()
        )

        reddit_instance.run(
            "cryptocurrency",
            limit=5
        )
    except KeyboardInterrupt as err:
        print("Gracefully exiting app...")
        sys.exit()