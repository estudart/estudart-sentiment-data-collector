import sys
import time
from datetime import datetime

from multiprocessing import Process

from src.queue.redis_queue_manager import RedisQueueManager
from src.models.crypto_prices.crypto_prices_model import CryptoPricesModel
from src.adapters.data_base_adapter import session
from src.utils.extensions import logger



def consume_queue():
    consumer_instance = RedisQueueManager()
    
    while True:
        queue_name = f"coinbase-trades-market-data"
        try:
            message = consumer_instance.consume_queue(queue_name)
            if message:
                message["ts"] = datetime.strptime(message.get("ts"),
                                                        '%Y-%m-%dT%H:%M:%S.%fZ')
                    
                message["src"] = "coinbase"
                logger.debug(f"Received message on queue: {message}")
                
                new_element = CryptoPricesModel(**message)
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
    try:
        Process(target=consume_queue).start()
    except KeyboardInterrupt as err:
        print("\nGracefully exiting app...")
        sys.exit()
