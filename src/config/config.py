from os.path import join
from os import getcwd, path
from configparser import ConfigParser

class Config:
    def __init__(self) -> None:
        self._lidar_ip = ""
        self._lidar_port = 0
        self._start_angle = 0
        self._stop_angle = 0
        self._distance = 0

    def read_config_file(self):
        try:
            config_dir = join(getcwd(), "conf", "config.ini")

            if not path.exists(config_dir):
                raise FileNotFoundError(f"O arquivo de configuração não foi encontrado em: {config_dir}")

            config = ConfigParser()
            config.read(config_dir)
            
            self._lidar_ip = str(config["LiDAR"]["ip"])
            self._lidar_port = int(config["LiDAR"]["port"])
            self._start_angle = int(config["LiDAR"]["start_angle"])
            self._stop_angle = int(config["LiDAR"]["stop_angle"])
            self._distance = int(config["LiDAR"]["distance"])
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
    def start_angle(self):
        return self._start_angle
    
    @property
    def stop_angle(self):
        return self._stop_angle
    
    @property
    def distance(self):
        return self._distance
    