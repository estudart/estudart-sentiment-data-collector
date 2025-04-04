import logging



class LoggerAdapter:
    def __init__(self, 
                 level=logging.INFO):
        self.level = level

        self.logger = None

        self._start_logger()

    def _start_logger(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(self.level)

        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def get_logger(self):
        return self.logger