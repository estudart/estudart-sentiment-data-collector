from datetime import datetime, timezone

from sqlalchemy import Column, String, Integer, Text, DateTime

from src.utils.extensions import Base



class YoutubeVideo(Base):
    __tablename__ = "youtube_videos"

    id = Column(String, primary_key=True)
    platform = Column(String, default="youtube", nullable=False)

    title = Column(String, default=None)
    description = Column(String, default=None)
    body = Column(Text, default=None)
    created_utc = Column(DateTime, default=None)
    channel_id = Column(String, default=None)
    channel_title = Column(String, default=None)
    topic = Column(String, nullable=False)
    
    view_count = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    num_comments = Column(Integer, default=0)
    num_favorite = Column(Integer, default=0)

    url = Column(String, default=None)

    # Metadata
    fetched_at = Column(DateTime, default=datetime.now(timezone.utc))

    def __repr__(self):
        return f"<YoutubeVideo(id={self.id})>"
