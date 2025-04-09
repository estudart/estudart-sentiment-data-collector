import sys
from multiprocessing import Process

from src.collectors.youtube_collector import YoutubeDataCollector
from src.utils.config import secrets


def start_scrapper(keyword_list):
    reddit_instance = YoutubeDataCollector()
    reddit_instance.run(keyword_list)

if __name__ == "__main__":
    try:
        for asset, asset_query_list in secrets.get("YOUTUBE_QUERYS").items():
                Process(target=start_scrapper, 
                        args=(asset_query_list, )
                        ).start()
    except KeyboardInterrupt as err:
        print("\nGracefully exiting app...")
        sys.exit()