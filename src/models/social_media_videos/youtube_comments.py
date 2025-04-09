from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from src.utils.extensions import Base


class YoutubeComment(Base):
    __tablename__ = "youtube_comments"

    id = Column(String, primary_key=True)
    video_id = Column(String, ForeignKey("youtube_videos.id"), nullable=True)
    author = Column(String, nullable=True)
    body = Column(Text, nullable=True)
    likes = Column(Integer, nullable=False)
    created_utc = Column(DateTime, nullable=False)

    video = relationship("YoutubeVideo", backref="comments")

    def __repr__(self):
        return (
            f"<YoutubeComment(id={self.id}, video_id={self.video_id}, author={self.author})>"
        )