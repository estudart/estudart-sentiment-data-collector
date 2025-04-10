from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from src.utils.extensions import Base


class RedditComment(Base):
    __tablename__ = "reddit_comments"

    id = Column(String, primary_key=True)  # Reddit comment ID
    post_id = Column(String, nullable=True)
    author = Column(String, nullable=True)
    body = Column(Text, nullable=True)
    likes = Column(Integer, nullable=True)
    created_utc = Column(DateTime, nullable=False)
    parent_id = Column(String, nullable=True)
    depth = Column(Integer, nullable=True)
    topic = Column(String, nullable=False)

    # Relationship to RedditPost (optional, but helpful)
    # post = relationship("RedditPost", backref="comments")

    def __repr__(self):
        return f"<RedditComment(id={self.id}, post_id={self.post_id}, author={self.author})>"