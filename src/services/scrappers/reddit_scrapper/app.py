from src.collectors.reddit_collector import RedditDataCollector
from src.queue.redis_queue_manager import RedisQueueManager



if __name__ == "__main__":
    reddit_instance = RedditDataCollector(
        RedisQueueManager()
    )

    reddit_instance.run(
        "cryptocurrency",
        limit=5
    )