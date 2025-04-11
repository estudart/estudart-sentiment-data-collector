from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from src.utils.extensions import Base


class WebsiteNewsModel(Base):
    __tablename__ = "website_news"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=True)
    subtitle = Column(String, nullable=True)
    body = Column(Text, nullable=True)
    topic = Column(String, nullable=False)
    created_utc = Column(DateTime, nullable=False)
    url = Column(String, default=None)

    def __repr__(self):
        return (
            f"<WebsiteNewsModel(id={self.id})>"
        )