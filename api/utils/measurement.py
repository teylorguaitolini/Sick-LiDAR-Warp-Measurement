from utils.config import Config
from utils.lms4000 import LMS4000
from utils.PointCloudManager import PointCloudManager
from utils.logger_config import logger
from utils.esp32Serial import ESP32Serial
from time import sleep

class Measurement:
    def __init__(self, conf:Config, DIR:str) -> None:
        self._conf = conf
        self._DIR = DIR
        self._warping = 0.0

    @property
    def warping(self):
        return self._warping
    
    def measuremt_rotine(self):
        try:
            logger.info("Starting measurement.")
            
            # --- Objeto que abstrai o sensor LiDAR X --- #
            lidar = LMS4000(self._conf.LMS4000_lidar_ip, self._conf.LMS4000_lidar_port, self._conf.LMS4000_start_angle, self._conf.LMS4000_stop_angle)

            # --- Objeto que abstrai a conexão serial com o ESP32 --- #
            esp32 = ESP32Serial(port="COM9")
            esp32.connect()

            if not esp32.is_connected:
                logger.error("ESP32 not connected.")
                return False
            
            esp32.send_command("start")
            sleep(1)

            response = esp32.read_response()
            logger.info(f"ESP32 response: {response}")

            if response != "starting":
                return False

            # Realiza a rotina de aquisição dos dados de scan
            sts = lidar.data_acquisition_routine()

            if not sts:
                logger.error("Error in data acquisition routine.")
                return False
            
            # --- Objeto PointCloudManager --- #
            pcm = PointCloudManager()

            # carrega a nuvem no pcm
            pcm.load_from_list(lidar.pcd)
            
            # Aplica filtros na nuvem
            pcm.filter_by_distance(self._conf.distance)

            # compute warping
            self._warping = pcm.WMUSS(self._conf.api_save, self._DIR)
            # pcm.WMLSS()

            esp32.disconnect()
                    
            return True
        except Exception as e:
            logger.error(f"Error in measurement routine: {e}""")
            return False