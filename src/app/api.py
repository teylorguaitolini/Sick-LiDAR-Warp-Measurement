import uvicorn
from config.config import Config
from sick.LMS4000.lms4000 import LMS4000
# from sick.LMS5xx.lms5xx import LMS5xx
from utils.PointCloudManager import PointCloudManager
from fastapi import FastAPI
from config.logger_config import logger

class Api:
    """
    Class for the API.
    """
    def __init__(self, conf:Config, DIR:str):
        self._DIR = DIR
        # --- FastAPI --- #
        self.app = FastAPI()
        # --- Dados do Arquivo de configuração --- #
        self._conf = conf

        # --- define the API routes --- #
        @self.app.post("/")
        async def measurement():
            logger.info("Measurement request received.")
            measurement_sts = self._measurement_rotine()
            if measurement_sts:
                logger.info("Warping Measurement Success")
                return {"message": "Warping Measurement Success"}
            else:
                logger.error("Warping Measurement Error.")
                return {"message": "Warping Measurement Error."}
        # --- --------------------- --- #
    
    def start(self):
        """
        # --- Start API --- #
        """
        try:
            uvicorn.run(
                        self.app, 
                        host=self._conf.api_host, 
                        port=self._conf.api_port,
                        log_config=None,  # Disable default Uvicorn logging configuration
                        log_level="info"
                    )
        except KeyboardInterrupt:
            logger.info("The API was finished by a KeyboardInterrupt.")

    def _measurement_rotine(self):
        """
        Método principal da rotina de medição
        """
        logger.info("Starting measurement.")

        # --- Objeto que abstrai o sensor LiDAR X --- #
        #self._lidar = LMS5xx(self._conf.LMS5xx_lidar_ip, self._conf.LMS5xx_lidar_port, self._conf.LMS5xx_start_angle, self._conf.LMS5xx_stop_angle)
        lidar = LMS4000(self._conf.LMS4000_lidar_ip, self._conf.LMS4000_lidar_port, self._conf.LMS4000_start_angle, self._conf.LMS4000_stop_angle)
        # --- Objeto PointCloudManager --- #
        pcm = PointCloudManager()

        # Realiza a rotina de aquisição dos dados de scan
        sts = lidar.data_acquisition_routine()

        if sts:
            try:
                # carrega a nuvem no pcm
                pcm.load_from_list(lidar.pcd)
                
                # Aplica filtros na nuvem
                pcm.filter_by_distance(self._conf.distance)

                # compute warping
                pcm.WMUSS(self._conf.api_save, self._DIR)
                # pcm.WMLSS()
                
                return True
            except Exception as e:
                logger.error(e)
                return False
        else:
            return False

    def _write_measurement_result(self, filename:str, warping_list:list):
        try:
            with open(filename, 'a') as file:
                file.write("# --- MEASUREMENT RESULT --- #\n")
                for i, warping in enumerate(warping_list):
                    file.write(f"Measured Warping by Method {i+1}: {(warping*100):.2f} cm\n")
                file.write("# ---")
                print(f"Mensagem gravada com sucesso em {filename}")
        except Exception as e:
            logger.error(f"Ocorreu um erro em write_measurement_result(): {e}")
