from os.path import join, exists
from configparser import ConfigParser
from config.logger_config import logger  # Import the logger

class Config:
    def __init__(self) -> None:
        # App
        self._app_save = False
        # Api
        self._api_save = False
        self._distance = 0
        # LMS4000
        self._LMS4000_lidar_ip = ""
        self._LMS4000_lidar_port = 0
        self._LMS4000_start_angle = 0
        self._LMS4000_stop_angle = 0
        # LMS5xx
        self._LMS5xx_lidar_ip = ""
        self._LMS5xx_lidar_port = 0
        self._LMS5xx_start_angle = 0
        self._LMS5xx_stop_angle = 0

    # --- App --- #    
    @property
    def app_save(self):
        return self._app_save
    
    # --- Api --- #
    @property
    def api_save(self):
        return self._api_save
    
    @property
    def distance(self):
        return self._distance
    
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
    
    # --- LMS5xx --- #
    @property
    def LMS5xx_lidar_ip(self):
        return self._LMS5xx_lidar_ip
    
    @property
    def LMS5xx_lidar_port(self):
        return self._LMS5xx_lidar_port
    
    @property
    def LMS5xx_start_angle(self):
        return self._LMS5xx_start_angle
    
    @property
    def LMS5xx_stop_angle(self):
        return self._LMS5xx_stop_angles

    def read_config_file(self, DIR:str):
        """
        Read the config.ini file.
        """
        try:
            config_dir = join(DIR, "conf", "config.ini")
            if not exists(config_dir):
                raise FileNotFoundError(f"The configuration file was not find in: {config_dir}")

            config = ConfigParser()
            config.read(config_dir)

            # App
            self._app_save = True if str(config["App"]["save"]).upper() == "TRUE" else False

            # Api
            self._api_save = True if str(config["Api"]["save"]).upper() == "TRUE" else False
            self._distance = int(config["Api"]["distance"])

            # LMS4000
            self._LMS4000_lidar_ip = str(config["LMS4000"]["ip"])
            self._LMS4000_lidar_port = int(config["LMS4000"]["port"])
            self._LMS4000_start_angle = int(config["LMS4000"]["start_angle"])
            self._LMS4000_stop_angle = int(config["LMS4000"]["stop_angle"])

            # LMS5xx
            self._LMS5xx_lidar_ip = str(config["LMS5xx"]["ip"])
            self._LMS5xx_lidar_port = int(config["LMS5xx"]["port"])
            self._LMS5xx_start_angle = int(config["LMS5xx"]["start_angle"])
            self._LMS5xx_stop_angle = int(config["LMS5xx"]["stop_angle"])

            logger.info("config.ini file was read successfuly.")

            return True
        except FileNotFoundError as e:
            logger.error(e)
            return False
        except Exception as e:
            logger.error(e)
            return False
        
    