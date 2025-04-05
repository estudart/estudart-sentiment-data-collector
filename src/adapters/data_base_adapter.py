from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from src.utils.extensions import Base
from src.models.social_media_posts.reddit_post import RedditPost
from src.utils.config import secrets



def create_connection():
    engine = create_engine(
        f"postgresql://{secrets.get('POSTGRES_USERNAME')}:"
        f"{secrets.get('POSTGRES_PASSWORD')}@{secrets.get('POSTGRES_HOST')}:"
        f"{secrets.get('POSTGRES_PORT')}/{secrets.get('POSTGRES_DB_NAME')}"
        f"?sslmode=require"
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

session = create_connection()