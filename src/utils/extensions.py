from src.adapters.logger_adapter import LoggerAdapter
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
logger = LoggerAdapter().get_logger()
