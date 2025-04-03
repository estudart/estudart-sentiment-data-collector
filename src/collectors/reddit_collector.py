import time
import json

import praw

from src.collectors.base_collector import DataCollector



class RedditDataCollector(DataCollector):
    def __init__(self, queue_manager):
        super().__init__(queue_manager)

        self.reddit = None

        self._initialize_credentials()

    
    def _initialize_credentials(self) -> None:
        self.reddit = praw.Reddit(
            client_id=self.secrets.get("REDDIT_CLIENT_ID"),
            client_secret=self.secrets.get("REDDIT_CLIENT_SECRET"),
            user_agent="python:sentiment-analyzer:v1.0 (by /u/yourusername)"
        )


    def fetch_data(self, keyword: str, limit: int = 10) -> list:
        posts = []

        sub_reddit_obj = self.reddit.subreddit(keyword)

        for post in sub_reddit_obj.hot(limit=limit):
            new_post = {
                # Textual Content
                "title": post.title,
                "selftext": post.selftext,
                "selftext_html": post.selftext_html,

                # Metadata
                "author": post.author_fullname,
                "subreddit": post.subreddit,
                "subreddit_prefixed": post.subreddit_name_prefixed,
                "domain": post.domain,
                "created_utc": post.created_utc,
                "edited": post.edited,

                # Engagement Metrics
                "score": post.score,
                "ups": post.ups,
                "downs": post.downs,
                "upvote_ratio": post.upvote_ratio,
                "total_awards_received": post.total_awards_received,
                "num_comments": post.num_comments,

                # Flair & Tags
                "link_flair_text": post.link_flair_text,
                "link_flair_richtext": post.link_flair_richtext,
                "author_flair_css_class": post.author_flair_css_class,

                # Governance & Voting Data (if applicable)
                "poll_data": post.poll_data if hasattr(post, "poll_data") else None,
                "governance_links": post.selftext if "governance" in post.selftext.lower() else None,

                # URL
                "url": post.url
            }

            posts.append(new_post)

            self.logger.info(f"Fetched post: {new_post}")

        return posts
    

    def process_data(self, data: dict):

        return json.dumps(data)
    

    def send_to_queue(self, data: json):
        
        return super().send_to_queue(data)
    

    def run(self, keyword: str, limit: int = 10):
        while True:
            self.fetch_data(keyword, limit=limit)
            time.sleep(5)
    
