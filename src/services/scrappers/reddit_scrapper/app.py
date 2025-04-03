import sys

from src.collectors.reddit_collector import RedditDataCollector



if __name__ == "__main__":
    try:
        reddit_instance = RedditDataCollector()

        reddit_instance.run(
            "cryptocurrency",
            limit=5
        )
    except KeyboardInterrupt as err:
        print("\nGracefully exiting app...")
        sys.exit()