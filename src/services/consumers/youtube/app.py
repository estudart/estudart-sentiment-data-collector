import sys
import time
from datetime import datetime, timezone

from multiprocessing import Process

from src.queue.redis_queue_manager import RedisQueueManager
from src.models.social_media_videos.youtube_video import YoutubeVideo
from src.models.social_media_videos.youtube_comments import YoutubeComment
from src.adapters.data_base_adapter import session
from src.utils.extensions import logger
from src.utils.config import secrets



def consume_queue(topic, topic_query_list, data_type):
    consumer_instance = RedisQueueManager()
    
    while True:
        for keyword in topic_query_list:
            queue_name = f"youtube-{keyword}-{data_type}"
            try:
                message = consumer_instance.consume_queue(queue_name)
                if message:
                    message["created_utc"] = datetime.strptime(message.get("created_utc"),
                                                            '%Y-%m-%dT%H:%M:%SZ')
                    message["topic"] = topic
                    logger.debug(f"Received message on queue: {message}")
                    
                    if data_type == "videos":
                        new_element = YoutubeVideo(**message)
                    elif data_type == "comments":
                        new_element = YoutubeComment(**message)
                    try:
                        logger.info(f"Prepared data: {message}")  
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
    for topic, topic_query_list in secrets.get("YOUTUBE_QUERYS").items():
        posts_consumer_process = Process(target=consume_queue,
                                        args=(
                                            topic,
                                            topic_query_list, 
                                            "videos",)
                                        ).start()
        comments_consumer_process = Process(target=consume_queue,
                                        args=(
                                            topic,
                                            topic_query_list, 
                                            "comments",)
                                        ).start()
