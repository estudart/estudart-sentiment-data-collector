import sys
import time

from multiprocessing import Process

from src.queue.redis_queue_manager import RedisQueueManager
from src.transformers.reddit_data_transformer import RedditDataTransformer
from src.models.social_media_posts.reddit_post import RedditPost
from src.models.social_media_posts.reddit_comments import RedditComment
from src.adapters.data_base_adapter import session
from src.utils.extensions import logger
from src.utils.config import secrets



def consume_queue(keyword, data_type):
    consumer_instance = RedisQueueManager()
    transformer_instance = RedditDataTransformer()
    queue_name = f"reddit-{keyword}-{data_type}"
    while True:
        try:
            message = consumer_instance.consume_queue(queue_name)
            if message:
                logger.debug(f"Received message on queue: {message}")
                normalized_message = transformer_instance.transform_data(
                    message, 
                    data_type)
                if data_type == "posts":
                    new_element = RedditPost(**normalized_message)
                elif data_type == "comments":
                    new_element = RedditComment(**normalized_message)
                try:
                    logger.info(f"Prepared data: {normalized_message}")  
                    session.add(new_element)
                    session.commit()
                except Exception as err:
                    session.rollback()
                    logger.error(f"Error saving post: {err}")    
            else:
                time.sleep(2)

        except KeyboardInterrupt as err:
            logger.info("Gracefully exiting app...")
            sys.exit()
        except Exception as err:
            logger.info(f"Could not consume queue, reason: {err}")


if __name__ == "__main__":
    for asset, asset_keyword_list in secrets.get("REDDIT_KEYWORDS").items():
        for keyword in asset_keyword_list:
            posts_consumer_process = Process(target=consume_queue,
                                            args=(keyword, "posts",)
                                            ).start()
            comments_consumer_process = Process(target=consume_queue,
                                            args=(keyword, "comments",)
                                            ).start()
