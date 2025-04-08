import sys
from multiprocessing import Process

from src.collectors.youtube_collector import YoutubeDataCollector
from src.utils.config import secrets


def start_scrapper(query):
    reddit_instance = YoutubeDataCollector()
    reddit_instance.run(query)

if __name__ == "__main__":
    try:
        for asset, asset_query_list in secrets.get("YOUTUBE_QUERYS").items():
            for query in asset_query_list:
                Process(target=start_scrapper, 
                        args=(query, )
                        ).start()
    except KeyboardInterrupt as err:
        print("\nGracefully exiting app...")
        sys.exit()