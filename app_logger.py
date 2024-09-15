import logging
import os

# Get log level from environment variable, defaulting to INFO
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()

# Set up logging based on environment variable
logging.basicConfig(level=getattr(logging, log_level, logging.INFO))

logger = logging.getLogger('app_logger')

logger.debug('Debug message')
logger.info('Info message')
logger.warning('Warning message')
logger.error('Error message')
logger.critical('Critical message')


def get_logger(name):
    return logging.getLogger(name)
