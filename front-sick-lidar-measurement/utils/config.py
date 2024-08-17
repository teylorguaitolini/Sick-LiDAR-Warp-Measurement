from configparser import ConfigParser
from os import getcwd
from os.path import join, exists

class Config:
    def __init__(self) -> None:
        # STREAMLIT
        self._STREAMLIT_port = 0
        # API-MOTOR
        self._API_MOTOR_port = 0
        # API-LIDAR
        self._API_LIDAR_port = 0
    
    # --- STREAMLIT --- #
    @property
    def STREAMLIT_port(self):
        return self._STREAMLIT_port
    # --- --- #
    
    # --- API-MOTOR --- #
    @property
    def API_MOTOR_port(self):
        return self._API_MOTOR_port
    # --- --- #

    # --- API-LIDAR --- #
    @property
    def API_LIDAR_port(self):
        return self._API_LIDAR_port
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

            # STREAMLIT
            self._STREAMLIT_port = config.getint("STREAMLIT", "port")
            # API-MOTOR
            self._API_MOTOR_port = config.getint("API-MOTOR", "port")
            # API-LIDAR
            self._API_LIDAR_port = config.getint("API-LIDAR", "port")

        except FileNotFoundError as e:
            raise FileNotFoundError(f"Error reading the configuration file: {e}")
        except Exception as e:
            raise Exception(f"Error reading the configuration file: {e}")
    