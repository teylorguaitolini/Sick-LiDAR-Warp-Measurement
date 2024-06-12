from os.path import join
from os import getcwd, path
from configparser import ConfigParser

class Config:
    def __init__(self) -> None:
        # LiDAR
        self._lidar_ip = ""
        self._lidar_port = 0
        self._start_angle = 0
        self._stop_angle = 0
        self._distance = 0
        # App
        self._scan = False
        self._save = False
        # Read the config file
        self._read_config_file()

    def _read_config_file(self):
        try:
            config_dir = join(getcwd(), "conf", "config.ini")

            if not path.exists(config_dir):
                raise FileNotFoundError(f"O arquivo de configuração não foi encontrado em: {config_dir}")

            config = ConfigParser()
            config.read(config_dir)
            # LiDAR
            self._lidar_ip = str(config["LiDAR"]["ip"])
            self._lidar_port = int(config["LiDAR"]["port"])
            self._start_angle = int(config["LiDAR"]["start_angle"])
            self._stop_angle = int(config["LiDAR"]["stop_angle"])
            self._distance = int(config["LiDAR"]["distance"])
            # App
            self._save = True if str(config["App"]["save"]).upper() == "TRUE" else False
            self._scan = True if str(config["App"]["scan"]).upper() == "TRUE" else False
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
    
    @property
    def scan(self):
        return self._scan
    
    @property
    def save(self):
        return self._save
    