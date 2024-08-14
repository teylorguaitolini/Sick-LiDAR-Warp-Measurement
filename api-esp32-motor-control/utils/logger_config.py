import logging
from logging.handlers import TimedRotatingFileHandler
from os import getcwd, makedirs
from os.path import exists, join

def setup_logger():
    log_dir = join(getcwd(), "logs")

    # Ensure the logs directory exists
    if not exists(log_dir):
        makedirs(log_dir)

    # Configure the root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Create a timed rotating file handler
    handler = TimedRotatingFileHandler(filename=join(log_dir, "api-esp32-motor-control.log"),
                                       when="midnight",
                                       interval=1,
                                       backupCount=7)
    handler.suffix = "%Y-%m-%d"
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

    # Set up Uvicorn logger
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.propagate = False  # Prevent double logging
    uvicorn_logger.setLevel(logging.INFO)
    for handler in logger.handlers:
        uvicorn_logger.addHandler(handler)

    return logger

logger = setup_logger()
