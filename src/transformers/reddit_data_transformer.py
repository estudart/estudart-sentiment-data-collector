from datetime import datetime, timezone
import json

from src.transformers.data_transformer import DataTransformer



class RedditDataTransformer(DataTransformer):
    def __init__(self):
        super().__init__()

        self.platform = "Reddit"

    
    def transform_data(self, data, data_type):
        if data_type == "posts":
            return {
                "id": data.get("post_id"),
                "title": data.get("title"),
                "body": data.get("selftext"),
                "selftext_html": data.get("selftext_html"),
                "author": data.get("author"),
                "subreddit": data.get("subreddit"),
                "subreddit_prefixed": data.get("subreddit_prefixed"),
                "url": data.get("url"),
                "created_utc": datetime.fromtimestamp(data.get("created_utc")),
                "score": data.get("score"),
                "upvotes": data.get("ups"),
                "downvotes": data.get("downs"),
                "num_comments": data.get("num_comments"),
                "link_flair_text": data.get("link_flair_text"),
                "link_flair_richtext": json.dumps(data.get("link_flair_richtext")),
                "author_flair_css_class": data.get("author_flair_css_class"),
                # Optional metadata
                "fetched_at": datetime.now(timezone.utc)
            }
        elif data_type == "comments":
            return {
                "id": data.get("comment_id"),
                "post_id": data.get("post_id"),
                "author": data.get("author"),
                "body": data.get("body"),
                "score": data.get("score"),
                "created_at": datetime.fromtimestamp(data.get("created_utc")),
                "parent_id": data.get("parent_id"),
                "depth": data.get("depth"),
            }
        else:
            raise Exception(f"Invalid data_type: {data_type}")