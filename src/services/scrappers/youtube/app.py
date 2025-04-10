import sys
from multiprocessing import Process

from src.collectors.youtube_collector import YoutubeDataCollector
from src.utils.config import secrets


def start_scrapper(topic_query_list):
    youtube_instance = YoutubeDataCollector()
    youtube_instance.run(topic_query_list)

if __name__ == "__main__":
    try:
        for topic, topic_query_list in secrets.get("YOUTUBE_QUERYS").items():
                Process(target=start_scrapper, 
                        args=(topic_query_list, )
                        ).start()
    except KeyboardInterrupt as err:
        print("\nGracefully exiting app...")
        sys.exit()