from os.path import join
from os import getcwd, path
from configparser import ConfigParser

class Config:
    def __init__(self) -> None:
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
        # App
        self._distance = 0
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
            
            # App
            self._distance = int(config["App"]["distance"])
            self._save = True if str(config["App"]["save"]).upper() == "TRUE" else False
            self._scan = True if str(config["App"]["scan"]).upper() == "TRUE" else False
        except FileNotFoundError as e:
            raise e
        except Exception as e:
            raise e
    
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
        return self._LMS5xx_stop_angle

    # --- App --- #
    @property
    def distance(self):
        return self._distance
    
    @property
    def scan(self):
        return self._scan
    
    @property
    def save(self):
        return self._save
    