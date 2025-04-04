from abc import ABC, abstractmethod



class DataTransformer(ABC):
    def __init__(self):
        super().__init__()

    
    @abstractmethod
    def transform_data(self, data: dict, data_type) -> dict:
        """
        Class designed to get data and normalize it.
        """
        pass