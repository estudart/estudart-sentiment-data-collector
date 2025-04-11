import time
import json
from datetime import datetime, timezone
from dateutil import parser as date_parser

import feedparser

from src.collectors.news_collector import NewsDataCollector



class RssDataCollector(NewsDataCollector):
    def __init__(self):
        super().__init__()

        self.platform = "rss"

        self.loop_delay_time = self.secrets.get("RSS_LOOP_DELAY_TIME")
        self.post_limit = self.secrets.get("RSS_POST_LIMIT")

    
    def _initialize_credentials(self) -> None:
        pass


    def normalize_entry(self, entry):
        title = getattr(entry, "title")
        url = getattr(entry, "link", None)
        raw_date = getattr(entry, "published")

        try:
            created_utc = date_parser.parse(raw_date).isoformat()
        except Exception:
            created_utc = date_parser.parse(raw_date[6:]).isoformat()

        body = None
        subtitle = None
            
        if hasattr(entry, "summary"):
            if hasattr(entry, "content"):
                body = entry.content[0].value
                subtitle = getattr(entry, "summary")
            else:
                body = getattr(entry, "summary")

        return {
            "title": title,
            "subtitle": subtitle,
            "body": body,
            "created_utc": created_utc,
            "url": url
        }


    def fetch_data(self, rss_url: str, limit: int) -> list:
        feed = feedparser.parse(rss_url)

        data_list = []

        for entry in feed.entries[:limit]:
            data_list.append(entry)
        
        return data_list
    
    def process_data(self, entry, keyword):
        is_new = False

        if not self.queue_manager.is_set_member(
            f"{self.platform}-processed-news", entry.title):

            processed_data = self.normalize_entry(entry)
            self.send_to_queue(
                f"{self.platform}-{keyword}-news", 
                processed_data)

            is_new = True

            self.logger.debug(f"Processed new article: {processed_data}")
        else:
            self.logger.debug(
                f"article {entry.title} already seen, skipping."
            )

        return is_new

    def send_to_queue(self, queue, data):
        return self.queue_manager.send_to_queue(queue, data)
    

    def run_loop(self, keyword):
        loop_start_time = datetime.now(timezone.utc)
        try:
            news = self.fetch_data(keyword, limit=self.post_limit)
        except Exception as err:
            self.logger.info(
                f"Could not fetch data for {keyword}, "
                f"reason: {err}"
            )
            raise

        number_of_news = 0
        for new in news:
            if self.process_data(new, keyword):
                number_of_news+=1
        loop_finished_time = datetime.now(timezone.utc)

        time_difference = (
            (loop_finished_time - loop_start_time)
            .total_seconds()
        )

        self.logger.info(
            f"Loop for {keyword} took {round(time_difference, 2)} seconds "
            f"and processed {number_of_news} posts."
        )


    def run(self, keywords):
        while True:
            for keyword in keywords:
                try:
                    self.run_loop(keyword)
                except Exception as err:
                    self.logger.error(
                        f"Could not run loop for {keyword}, reason: {err}"
                    )
            
            time.sleep(self.loop_delay_time)   
