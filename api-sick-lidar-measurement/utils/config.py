from configparser import ConfigParser
from os import getcwd
from os.path import join, exists

class Config:
    def __init__(self) -> None:
        # API
        self._API_port = 0
        # LMS4000
        self._LMS4000_ip = ""
        self._LMS4000_port = 0
        # Parameters
        self._response_time = 0.0
        self._pulses_per_rev = 0
        self._mm_per_rev = 0.0
        self._start_angle = 0
        self._stop_angle = 0
        self._distance = 0.0
        self._filter_Y_iterations_num = 0
        self._reverse_direction = False
        self._save_point_cloud = False
    
    # --- API --- #
    @property
    def API_port(self):
        return self._API_port
    # --- --- #
    
    # --- LMS4000 --- #
    @property
    def LMS4000_ip(self):
        return self._LMS4000_ip
    
    @property
    def LMS4000_port(self):
        return self._LMS4000_port
    # --- --- #

    # --- PARAMETERS --- #    
    @property
    def response_time(self):
        return self._response_time
    
    @property
    def pulses_per_rev(self):
        return self._pulses_per_rev
    
    @property
    def mm_per_rev(self):
        return self._mm_per_rev
    
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
    def filter_Y_iterations_num(self):
        return self._filter_Y_iterations_num
    
    @property
    def reverse_direction(self):
        return self._reverse_direction
    
    @property
    def save_point_cloud(self):
        return self._save_point_cloud
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
            self._API_port = config.getint("API", "port")

            # LMS4000
            self._LMS4000_ip = config.get("LMS4000", "ip")
            self._LMS4000_port = config.getint("LMS4000", "port")

            # PARAMETERS
            self._response_time = config.getfloat("PARAMETERS", "response_time")
            self._pulses_per_rev = config.getint("PARAMETERS", "pulses_per_rev")
            self._mm_per_rev = config.getfloat("PARAMETERS", "mm_per_rev")
            self._start_angle = config.getint("PARAMETERS", "start_angle")
            self._stop_angle = config.getint("PARAMETERS", "stop_angle")
            self._distance = config.getfloat("PARAMETERS", "distance")
            self._filter_Y_iterations_num = config.getint("PARAMETERS", "filter_Y_iterations_num")
            self._reverse_direction = True if config.get("PARAMETERS", "reverse_direction").upper() == "TRUE" else False
            self._save_point_cloud = True if config.get("PARAMETERS", "save_point_cloud").upper() == "TRUE" else False

        except FileNotFoundError as e:
            raise FileNotFoundError(f"Error reading the configuration file: {e}")
        except Exception as e:
            raise Exception(f"Error reading the configuration file: {e}")
    