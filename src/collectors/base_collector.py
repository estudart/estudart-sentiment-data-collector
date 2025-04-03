from abc import ABC, abstractmethod
import json

from src.queue.queue_manager import QueueManager
from src.utils.config import secrets
from src.adapters.logger_adapter import LoggerAdapter



class DataCollector(ABC):
    def __init__(self,
                 queue_manager: QueueManager,
                 secrets: dict = secrets):
        
        self.queue_manager = queue_manager
        self.logger = LoggerAdapter().get_logger()
        self.secrets = secrets

    @abstractmethod
    def _initialize_credentials(self) -> None:
        """
        Classes should implement this method in order to initialize
        credentials.
        """
        pass


    @abstractmethod
    def fetch_data(self, keyword: str, limit: int = 10) -> list:
        """
        Fetches data from the source.
        """
        pass


    @abstractmethod
    def process_data(self, data: dict) -> dict:
        """
        Processes a single data into a structured format.
        """
        pass

    
    @abstractmethod
    def send_to_queue(self, data: json) -> None:
        """
        Sends processed data to the queue for further processing.
        """
        pass


    @abstractmethod
    def run(self, keyword: str, limit: int = 10) -> None:
        """
        Main method that fetches, processes, and queues data.
        """
        pass