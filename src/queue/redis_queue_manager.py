import json

import redis

from src.queue.queue_manager import QueueManager


class RedisQueueManager(QueueManager):
    def __init__(self):
        super().__init__()
        
        self.host = self.secrets.get("REDIS_HOST")
        self.port = self.secrets.get("REDIS_PORT")
        

        self.queue_connection = None

        self._initialize_connection()

    
    def _initialize_connection(self):
        try:
            # Connect to Redis
            self.queue_connection = redis.Redis(
                    host=self.host,
                    port=self.port
                    )
            
            # Check connection
            self.queue_connection.ping()
            self.logger.info(
                "Connection with Redis was established, "
                f"host: {self.host}:{self.port}"
            )
        except Exception as err:
            self.logger.error(f"Could not connect to Redis: {err}")

    
    def send_to_queue(self, queue_name: str, data: dict):
        self.queue_connection.lpush(queue_name, json.dumps(data))
        self.logger.info(f"Message was sent to queue: {data}")

    
    def consume_queue(self, queue_name: str):
        data = self.queue_connection.rpop(queue_name)
        if data:
            data_json = json.loads(data)
            self.logger.debug(f"Data received from queue: {data_json}")
            return data_json
        return False
    

    def store_to_db(self, data_json: json) -> None:
        try:
            self.logger.info(
                f"Data is perfect, storing it to DataBase: {data_json}")
        except Exception as err:
            self.logger.error(
                f"Data is bad, reason: {err}")

    
    def run(self, queue_name):
        while True:
            queue_data = self.consume_queue(self, queue_name)
            if queue_data:
                self.store_to_db(queue_data)
