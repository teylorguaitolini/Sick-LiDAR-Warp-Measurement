from os.path import exists
from configparser import ConfigParser
from utils.logger_config import logger

class Config:
    def __init__(self) -> None:
        # Api
        self._api_host = ""
        self._api_port = 0
        self._api_save = False
        self._distance = 0
        # LMS4000
        self._LMS4000_lidar_ip = ""
        self._LMS4000_lidar_port = 0
        self._LMS4000_start_angle = 0
        self._LMS4000_stop_angle = 0
    
    # --- Api --- #
    @property
    def api_host(self):
        return self._api_host
    
    @property
    def api_port(self):
        return self._api_port

    @property
    def api_save(self):
        return self._api_save
    
    @property
    def distance(self):
        return self._distance
    # --- --- #
    
    # --- LMS4000 --- #
    @property
    def LMS4000_lidar_ip(self):
        return self._LMS4000_lidar_ip
    
    @property
    def LMS4000_lidar_port(self):
        return self._LMS4000_lidar_port
    
    @property
    def LMS4000_start_angle(self):
        return self._LMS4000_start_angle
    
    @property
    def LMS4000_stop_angle(self):
        return self._LMS4000_stop_angle
    # --- --- #

    def read_config_file(self, DIR:str):
        """
        Read the config.ini file.
        """
        try:
            if not exists(DIR):
                raise FileNotFoundError(f"The configuration file was not find in: {DIR}")

            config = ConfigParser()
            config.read(DIR)

            # Api
            self._api_host = str(config["Api"]["host"])
            self._api_port = int(config["Api"]["port"])
            self._api_save = True if str(config["Api"]["save"]).upper() == "TRUE" else False
            self._distance = int(config["Api"]["distance"])

            # LMS4000
            self._LMS4000_lidar_ip = str(config["LMS4000"]["ip"])
            self._LMS4000_lidar_port = int(config["LMS4000"]["port"])
            self._LMS4000_start_angle = int(config["LMS4000"]["start_angle"])
            self._LMS4000_stop_angle = int(config["LMS4000"]["stop_angle"])

            logger.info("config.ini file was read successfuly.")

            return True
        except FileNotFoundError as e:
            logger.error(e)
            return False
        except Exception as e:
            logger.error(e)
            return False
    