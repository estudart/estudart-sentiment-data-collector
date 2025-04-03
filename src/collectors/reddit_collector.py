import time
import json

import praw

from src.collectors.base_collector import DataCollector



class RedditDataCollector(DataCollector):
    def __init__(self):
        super().__init__()

        self.reddit = None

        self._initialize_credentials()

    
    def _initialize_credentials(self) -> None:
        self.reddit = praw.Reddit(
            client_id=self.secrets.get("REDDIT_CLIENT_ID"),
            client_secret=self.secrets.get("REDDIT_CLIENT_SECRET"),
            user_agent="python:sentiment-analyzer:v1.0 (by /u/yourusername)"
        )


    def fetch_data(self, keyword: str, limit: int = 10) -> list:
        sub_reddit_obj = self.reddit.subreddit(keyword)
        hot_posts = sub_reddit_obj.hot(limit=limit)
        return hot_posts
    

    def process_data(self, post: dict, keyword: str) -> list:
        is_post_processed = False
        is_comments_processed = False

        try:
            # Process post and send to queue
            processed_post = json.dumps({
                # Textual Content
                "title": post.title,
                "selftext": post.selftext,
                "selftext_html": post.selftext_html,

                # Metadata
                "post_id": post.id,
                "author": str(post.author_fullname),
                "subreddit": str(post.subreddit),
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

                # URL
                "url": post.url
            })
            self.send_to_queue(f"reddit-{keyword}-posts", 
                                processed_post)
            is_post_processed = True
        except Exception as err:
            self.logger.error(
                f"Could not process post with id {post.id}, "
                f"reason: {err}")

        try:
            # Get all comments for the post
            post.comments.replace_more(limit=10)
            comments = post.comments.list()
            # Run a loop on comments list and send it to queue
            for comment in comments:
                processed_comments = json.dumps({
                    "comment_id": comment.id,
                    "post_id": post.id,
                    "author": str(comment.author),
                    "body": comment.body,
                    "score": comment.score,
                    "created_utc": comment.created_utc,
                    "parent_id": comment.parent_id,
                    "depth": comment.depth  # Helps in structuring nested comments
                })
                self.send_to_queue(f"reddit-{keyword}-comments", 
                                    processed_comments)
            is_comments_processed = True
        except Exception as err:
            self.logger.error(
                f"Could not process comments for post with id {post.id}, "
                f"reason: {err}")

        return (is_post_processed, is_comments_processed)
    

    def send_to_queue(self, queue, data: json):
        return self.queue_manager.send_to_queue(queue, data)
    

    def run(self, keyword: str, limit: int = 10):
        while True:
            posts = self.fetch_data(keyword, limit=limit)
            for post in posts:
                self.process_data(post, keyword)
            time.sleep(60)
