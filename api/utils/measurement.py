from utils.config import Config
from utils.lms4000 import LMS4000
from utils.PointCloudManager import PointCloudManager
from utils.logger_config import logger

class Measurement:
    def __init__(self, conf:Config, DIR:str) -> None:
        self._conf = conf
        self._DIR = DIR
        self._warping = 0.0

    @property
    def warping(self):
        return self._warping
    
    def measuremt_rotine(self):
        logger.info("Starting measurement.")
        
        # --- Objeto que abstrai o sensor LiDAR X --- #
        lidar = LMS4000(self._conf.LMS4000_lidar_ip, self._conf.LMS4000_lidar_port, self._conf.LMS4000_start_angle, self._conf.LMS4000_stop_angle)

        # Realiza a rotina de aquisição dos dados de scan
        sts = lidar.data_acquisition_routine()

        if sts:
            try:
                # --- Objeto PointCloudManager --- #
                pcm = PointCloudManager()

                # carrega a nuvem no pcm
                pcm.load_from_list(lidar.pcd)
                
                # Aplica filtros na nuvem
                pcm.filter_by_distance(self._conf.distance)

                # compute warping
                self._warping = pcm.WMUSS(self._conf.api_save, self._DIR)
                # pcm.WMLSS()
                
                return True
            except Exception as e:
                logger.error(e)
                return False
        else:
            return False