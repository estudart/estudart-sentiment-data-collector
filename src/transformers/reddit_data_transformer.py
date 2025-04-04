from datetime import datetime

from src.transformers.data_transformer import DataTransformer



class RedditDataTransformer(DataTransformer):
    def __init__(self):
        super().__init__()

        self.platform = "Reddit"

    
    def transform_data(self, data, data_type):
        if data_type == "posts":
            return {
                "post_id": data.get("post_id"),
                "platform": self.platform,
                "title": data.get("title"),
                "body": data.get("selftext"),
                "body_html": data.get("selftext_html"),
                "author": data.get("author"),
                "community": data.get("subreddit"),
                "community_prefixed": data.get("subreddit_prefixed"),
                "source_domain": data.get("domain"),
                "created_at": datetime.fromtimestamp(data.get("created_utc")),
                "edited": data.get("edited"),  # JSON-safe (bool or timestamp)
                "score": data.get("score"),
                "upvotes": data.get("ups"),
                "downvotes": data.get("downs"),
                "upvote_ratio": data.get("upvote_ratio"),
                "awards": data.get("total_awards_received"),
                "comment_count": data.get("num_comments"),
                "flair_text": data.get("link_flair_text"),
                "flair_richtext": data.get("link_flair_richtext"),
                "author_flair_class": data.get("author_flair_css_class"),
                "external_url": data.get("url"),
            }
        elif data_type == "comments":
            return {
                "comment_id": data.get("comment_id"),
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