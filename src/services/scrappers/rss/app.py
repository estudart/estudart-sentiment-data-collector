import sys
from multiprocessing import Process

from src.collectors.rss_collector import RssDataCollector
from src.utils.config import secrets


def start_scrapper(news_url_list):
    rss_instance = RssDataCollector()
    rss_instance.run(news_url_list)

if __name__ == "__main__":
    try:
        for new, news_url_list in secrets.get("NEWS_WEBSITES_URLS").items():
            Process(target=start_scrapper, 
                    args=(news_url_list, )
                    ).start()
    except KeyboardInterrupt as err:
        print("\nGracefully exiting app...")
        sys.exit()