from abc import ABC, abstractmethod

from src.adapters.logger_adapter import LoggerAdapter
from src.utils.config import secrets



class QueueManager(ABC):
    def __init__(self):
        
        self.secrets = secrets
        
        self.logger = LoggerAdapter().get_logger()

        self.queue_connection = None

    
    @abstractmethod
    def _initialize_connection(self):
        """
        Start connection given credentials.
        """
        pass

    
    @abstractmethod
    def send_to_queue(self, queue_name: str, data: dict):
        """
        Sends data to a queue.
        """
        pass


    @abstractmethod
    def consume_queue(self):
        """
        Consumes from queue.
        """
        pass


    @abstractmethod
    def store_to_db(self):
        """
        Stores processed data into database.
        """
        pass 


    @abstractmethod
    def run(self):
        """
        Main method that consumes, processes, and store in database.
        """
        pass