import sys
import time

from multiprocessing import Process

from src.queue.redis_queue_manager import RedisQueueManager
from src.utils.extensions import logger
from src.utils.config import secrets



def consume_queue(queue_name):
    consumer_instance = RedisQueueManager()
    while True:
        try:
            message = consumer_instance.consume_queue(queue_name)
            if message:
                logger.debug(f"Received message on queue: {message}")
            else:
                time.sleep(2)
        except KeyboardInterrupt as err:
            logger.info("Gracefully exiting app...")
            sys.exit()
        except Exception as err:
            logger.info(f"Could not consume queue, reason: {err}")


if __name__ == "__main__":
    for queue in secrets.get("QUEUES"):
        posts_consumer_process = Process(target=consume_queue,
                                        args=(queue,)
                                        ).start()

