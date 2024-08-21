from configparser import ConfigParser
from os import getcwd
from os.path import join, exists

class Config:
    def __init__(self) -> None:
        # API
        self._API_host = ""
        self._API_port = 0
        self._distance = 0.0
        # LMS4000
        self._LMS4000_lidar_ip = ""
        self._LMS4000_lidar_port = 0
        self._LMS4000_start_angle = 0
        self._LMS4000_stop_angle = 0
    
    # --- API --- #
    @property
    def API_host(self):
        return self._API_host
    
    @property
    def API_port(self):
        return self._API_port
    
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

    def read_config_file(self):
        """
        Read the config.ini file.
        """
        try:
            DIR = join(getcwd(), "config.ini")

            if not exists(DIR):
                raise FileNotFoundError(f"The configuration file was not find in: {DIR}")

            config = ConfigParser()
            config.read(DIR)

            # API
            self._API_host = str(config["API"]["host"])
            self._API_port = int(config["API"]["port"])
            self._distance = float(config["API"]["distance"])

            # LMS4000
            self._LMS4000_lidar_ip = str(config["LMS4000"]["ip"])
            self._LMS4000_lidar_port = int(config["LMS4000"]["port"])
            self._LMS4000_start_angle = int(config["LMS4000"]["start_angle"])
            self._LMS4000_stop_angle = int(config["LMS4000"]["stop_angle"])

        except FileNotFoundError as e:
            raise FileNotFoundError(f"Error reading the configuration file: {e}")
        except Exception as e:
            raise Exception(f"Error reading the configuration file: {e}")
    