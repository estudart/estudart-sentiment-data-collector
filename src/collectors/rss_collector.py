import time
import json
from datetime import datetime, timezone
from dateutil import parser as date_parser

import feedparser

from src.collectors.news_collector import NewsDataCollector



class RssDataCollector(NewsDataCollector):
    def __init__(self):
        super().__init__()

        self.loop_delay_time = self.secrets.get("RSS_LOOP_DELAY_TIME")
        self.post_limit = self.secrets.get("RSS_POST_LIMIT")

    
    def _initialize_credentials(self) -> None:
        pass


    def normalize_entry(self, entry):
        # Try to safely get content/body
        body = None
        if hasattr(entry, "content") and entry.content:
            body = entry.content[0].value
        elif hasattr(entry, "summary"):
            body = entry.summary

        # Try to get a valid timestamp
        created_utc = None
        for date_field in ["published", "updated", "created"]:
            if hasattr(entry, date_field):
                try:
                    created_utc = date_parser.parse(getattr(entry, date_field)).isoformat()
                    break
                except Exception as err:
                    self.logger.error(f"Could not parse datetime: {err}")
                    pass

        return {
            "title": getattr(entry, "title", ""),
            "description": getattr(entry, "description", getattr(entry, "summary", "")),
            "body": body,
            "created_utc": created_utc,
            "url": getattr(entry, "link", ""),
        }


    def fetch_data(self, rss_url: str, limit: int) -> list:
        feed = feedparser.parse(rss_url)

        data_list = []

        for entry in feed.entries[:limit]:
            data_list.append(entry)
        
        return data_list
    
    def process_data(self, data):
        is_new = False
        # check if news were sent already

        processed_data = self.normalize_entry(data)

        # # if not send it to queue
        # self.queue_manager.send_to_queue(
        #     "all-news", 
        #     processed_data
        # )

        self.logger.info(f"New article to process: {processed_data}")
        return is_new

    def send_to_queue(self, queue, data: json):
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
            if self.process_data(new):
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
                        f"Could not run loop for {keyword}, reson: {err}"
                    )
            
            time.sleep(self.loop_delay_time)   
