import sys
from config.config import Config
from app.app import App
from app.api import Api
from config.logger_config import logger  # Import the logger
from os.path import dirname
from os import getcwd

if __name__ == "__main__":
    """
    Manage the flow of execution.

    bash: python main.py api - to execute the API

    bash: python main.py app - to execute the APP
    """    
    DIR = dirname(getcwd())    # Main directory

    conf = Config()
    conf_sts = conf.read_config_file(DIR)

    if conf_sts:
        if len(sys.argv) > 1:
            if sys.argv[1] == "api":
                logger.info("Starting API...")
                api = Api(conf, DIR)
                api.start()

            elif sys.argv[1] == "app":
                logger.info("Starting App...")
                app = App(conf)
                app.start()

            else:
                logger.error(f"Unknown parameter: {sys.argv[1]}")

        else:
            logger.error("No parameter has been passed to initialize.")
