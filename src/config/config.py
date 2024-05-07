from os.path import join
from os import getcwd, path
from configparser import ConfigParser

class Config:
    def __init__(self) -> None:
        self._lidar_ip = ""
        self._lidar_port = 0
        self._min_angle = 0
        self._max_angle = 0

    def read_config_file(self):
        try:
            config_dir = join(getcwd(), "conf", "config.ini")

            if not path.exists(config_dir):
                raise FileNotFoundError(f"O arquivo de configuração não foi encontrado em: {config_dir}")

            config = ConfigParser()
            config.read(config_dir)
            
            self._lidar_ip = str(config["LiDAR"]["ip"])
            self._lidar_port = int(config["LiDAR"]["port"])
            self._min_angle = int(config["LiDAR"]["min_angle"])
            self._max_angle = int(config["LiDAR"]["max_angle"])
        except FileNotFoundError as e:
            raise e
        except Exception as e:
            raise e
    
    @property
    def lidar_ip(self):
        return self._lidar_ip
    
    @property
    def lidar_port(self):
        return self._lidar_port
    
    @property
    def min_angle(self):
        return self._min_angle
    
    @property
    def max_angle(self):
        return self._max_angle