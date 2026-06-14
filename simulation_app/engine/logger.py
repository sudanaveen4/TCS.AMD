import logging
import os

LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'shiftsense_system.log')

# Configure the global logger
logger = logging.getLogger("ShiftSense")
logger.setLevel(logging.DEBUG)

# Create file handler
fh = logging.FileHandler(LOG_FILE, encoding='utf-8')
fh.setLevel(logging.DEBUG)

# Create console handler
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# Add handlers
if not logger.handlers:
    logger.addHandler(fh)
    logger.addHandler(ch)

def get_system_logger():
    return logger
