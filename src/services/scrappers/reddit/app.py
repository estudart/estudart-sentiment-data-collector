import sys
from multiprocessing import Process

from src.collectors.reddit_collector import RedditDataCollector
from src.utils.config import secrets


def start_scrapper(asset_keyword_list):
    reddit_instance = RedditDataCollector()
    reddit_instance.run(asset_keyword_list)

if __name__ == "__main__":
    try:
        for asset, asset_keyword_list in secrets.get("REDDIT_KEYWORDS").items():
            Process(target=start_scrapper, 
                    args=(asset_keyword_list, )
                    ).start()
    except KeyboardInterrupt as err:
        print("\nGracefully exiting app...")
        sys.exit()