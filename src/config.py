from os.path import join
from os import getcwd
from configparser import ConfigParser

class Config:
    def __init__(self) -> None:
        self.conf_sts = False

        self.lidar_ip = ""
        self.lidar_port = 0
        self.min_angle = 0
        self.max_angle = 0
        self.scan_time = 0

    def read_config_file(self):
        try:
            path = join(getcwd(), "conf", "config.ini")

            config = ConfigParser()
            config.read(path)
            
            self.lidar_ip = str(config["LiDAR"]["ip"])
            self.lidar_port = int(config["LiDAR"]["port"])
            self.min_angle = int(config["LiDAR"]["min_angle"])
            self.max_angle = int(config["LiDAR"]["max_angle"])
            self.scan_time = int(config["LiDAR"]["scan_time"])

            self.conf_sts = True
        except:
            self.conf_sts = False