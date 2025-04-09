import time
import json
from datetime import datetime, timezone

import praw

from src.collectors.base_collector import DataCollector
from concurrent.futures import ThreadPoolExecutor, as_completed



class RedditDataCollector(DataCollector):
    def __init__(self):
        super().__init__()

        self.loop_delay_time = self.secrets.get("REDDIT_LOOP_DELAY_TIME")
        self.post_limit = self.secrets.get("REDDIT_POST_LIMIT")
        self.comment_limit = self.secrets.get("REDDIT_COMMENT_LIMIT")
        self.executor = ThreadPoolExecutor(max_workers=5)

        self.reddit = None

        self._initialize_credentials()

    
    def _initialize_credentials(self) -> None:
        self.reddit = praw.Reddit(
            client_id=self.secrets.get("REDDIT_CLIENT_ID"),
            client_secret=self.secrets.get("REDDIT_CLIENT_SECRET"),
            user_agent="python:sentiment-analyzer:v1.0 (by /u/yourusername)"
        )


    def fetch_data(self, keyword: str, limit: int) -> list:
        sub_reddit_obj = self.reddit.subreddit(keyword)
        hot_posts = sub_reddit_obj.hot(limit=limit)
        new_posts = sub_reddit_obj.new(limit=limit)
        return list(hot_posts) + list(new_posts)
    

    def process_comment(self, comment, keyword, post_id):
        processed_comments = {
            "comment_id": comment.id,
            "post_id": post_id,
            "author": str(comment.author),
            "body": comment.body,
            "score": comment.score,
            "created_utc": comment.created_utc,
            "parent_id": comment.parent_id,
            "depth": comment.depth  # Helps in structuring nested comments
        }
        if not self.queue_manager.is_set_member("reddit-comments", comment.id):
            self.send_to_queue(f"reddit-{keyword}-comments", 
                                processed_comments)
    

    def process_data(self, post: dict, keyword: str) -> list:
        is_post_new = False

        try:
            # Process post and send to queue
            processed_post = {
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
            }
            if not self.queue_manager.is_set_member("reddit-posts", post.id):
                self.send_to_queue(f"reddit-{keyword}-posts", 
                                    processed_post)
                is_post_new = True
            else:
                self.logger.debug(f"Post {post.id} already seen, skipping.")
                return is_post_new
        except Exception as err:
            self.logger.error(
                f"Could not process post with id {post.id}, "
                f"reason: {err}")

        try:
            # Get all comments for the post
            post.comments.replace_more(limit=self.comment_limit)
            comments = post.comments.list()
            # Run a loop on comments list and send it to queue
            futures = [
                self.executor.submit(self.process_comment, 
                                     comment, keyword, post.id)
                for comment in comments
            ]
            for future in as_completed(futures):
                future.result()

        except Exception as err:
            self.logger.error(
                f"Could not process comments for post with id {post.id}, "
                f"reason: {err}")

        return is_post_new
    

    def send_to_queue(self, queue, data: json):
        return self.queue_manager.send_to_queue(queue, data)
    

    def run_loop(self, keyword):
        loop_start_time = datetime.now(timezone.utc)
        try:
            posts = self.fetch_data(keyword, limit=self.post_limit)
        except Exception as err:
            self.logger.info(
                f"Could not fetch data for {keyword}, "
                f"reason: {err}"
            )
            raise

        number_of_posts = 0
        for post in posts:
            if self.process_data(post, keyword):
                number_of_posts+=1
        loop_finished_time = datetime.now(timezone.utc)

        time_difference = (
            (loop_finished_time - loop_start_time)
            .total_seconds()
        )

        self.logger.info(
            f"Loop for {keyword} took {round(time_difference, 2)} seconds "
            f"and processed {number_of_posts} posts."
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
