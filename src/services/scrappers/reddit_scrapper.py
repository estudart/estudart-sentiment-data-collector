import sys
from multiprocessing import Process

from src.collectors.reddit_collector import RedditDataCollector
from src.utils.config import secrets


def start_scrapper(keyword):
    reddit_instance = RedditDataCollector()
    reddit_instance.run(keyword)

if __name__ == "__main__":
    try:
        for keyword in secrets.get("KEYWORDS"):
            Process(target=start_scrapper, 
                    args=(keyword, )
                    ).start()
    except KeyboardInterrupt as err:
        print("\nGracefully exiting app...")
        sys.exit()