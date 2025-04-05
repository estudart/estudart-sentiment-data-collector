from datetime import datetime, timezone

from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime

from src.utils.extensions import Base



class RedditPost(Base):
    __tablename__ = "reddit_posts"

    id = Column(String, primary_key=True)  # Reddit post ID
    platform = Column(String, default="reddit", nullable=False)

    # Campos comuns
    title = Column(String, default=None)
    body = Column(Text, default=None)
    author = Column(String, default=None)
    url = Column(String, default=None)
    created_utc = Column(DateTime, default=None)
    is_reply = Column(Boolean, default=False)
    score = Column(Integer, default=0)
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    num_comments = Column(Integer, default=0)

    # Campos específicos do Reddit
    selftext_html = Column(Text, default=None)
    subreddit = Column(String, default=None)
    subreddit_prefixed = Column(String, default=None)
    link_flair_text = Column(String, default=None)
    link_flair_richtext = Column(Text, default=None)  # JSON como string
    author_flair_css_class = Column(String, default=None)

    # Metadata
    fetched_at = Column(DateTime, default=datetime.now(timezone.utc))

    def __repr__(self):
        return f"<RedditPost(id={self.id}, subreddit={self.subreddit})>"
