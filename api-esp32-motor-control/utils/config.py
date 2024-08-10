from configparser import ConfigParser
from os import getcwd
from os.path import join, exists

class Config:
    def __init__(self) -> None:
        # ESP32
        self._com_port = ""
        self._baud_rate = 0
        self._timeout = 0
        # API
        self._host = ""
        self._port = 0

    @property
    def com_port(self):
        return self._com_port
    
    @property
    def baud_rate(self):
        return self._baud_rate
    
    @property
    def timeout(self):
        return self._timeout
    
    @property
    def host(self):
        return self._host
    
    @property
    def port(self):
        return self._port
    
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

            # ESP32
            self._com_port = str(config["ESP32"]["com_port"])
            self._baud_rate = int(config["ESP32"]["baud_rate"])
            self._timeout = int(config["ESP32"]["timeout"])

            # API
            self._host = str(config["API"]["host"])
            self._port = int(config["API"]["port"])

        except FileNotFoundError as e:
            raise FileNotFoundError(f"Error reading the configuration file: {e}")
        except Exception as e:
            raise Exception(f"Error reading the configuration file: {e}")
    