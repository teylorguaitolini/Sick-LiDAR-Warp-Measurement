from config.config import Config
from datetime import datetime
from os.path import join, exists
from os import getcwd, makedirs
from sick.LMS4000 import LMS4000
#from sick.LMS5xx import LMS5xx
from utils.PointCloudManager import PointCloudManager
from fastapi import FastAPI, HTTPException

class Api:
    """
    Class for the API.
    """
    def __init__(self, conf:Config):
        # --- FastAPI --- #
        self.app = FastAPI()
        # --- Dados do Arquivo de configuração --- #
        self._conf = conf

        # define the API routes
        self._setup()

    def _setup(self):
        """
        To define all the API routes here.
        """
        @self.app.post("/")
        async def start():
            try:
                self._measurement_rotine()
                return {"message": "Warping Measurement done."}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
    
    def _write_measurement_result(self, filename:str, warping_list:list):
        try:
            with open(filename, 'a') as file:
                file.write("# --- MEASUREMENT RESULT --- #\n")
                for i, warping in enumerate(warping_list):
                    file.write(f"Measured Warping by Method {i+1}: {(warping*100):.2f} cm\n")
                file.write("# ---")
                print(f"Mensagem gravada com sucesso em {filename}")
        except Exception as e:
            print(f"Ocorreu um erro em write_measurement_result(): {e}")
            
    def _measurement_rotine(self):
        """
        Método principal da rotina de medição
        """
        # --- Objeto que abstrai o sensor LiDAR X --- #
        #self._lidar = LMS5xx(self._conf.LMS5xx_lidar_ip, self._conf.LMS5xx_lidar_port, self._conf.LMS5xx_start_angle, self._conf.LMS5xx_stop_angle)
        lidar = LMS4000(self._conf.LMS4000_lidar_ip, self._conf.LMS4000_lidar_port, self._conf.LMS4000_start_angle, self._conf.LMS4000_stop_angle)
        # --- Objeto PointCloudManager --- #
        pcm = PointCloudManager()

        # Realiza a rotina de aquisição dos dados de scan
        pcd = lidar.data_acquisition_routine()

        # carrega a nuvem no pcm
        pcm.load_from_list(pcd)

        # caso seja para salvar, cria o diretorio se não existir
        if self._conf.api_save:
            file_dir = join(getcwd(), "Measurements", str(datetime.now().strftime('%Y%m%d_%H%M%S')))
            if not exists(file_dir):
                makedirs(file_dir)

            # caso seja para salvar, salva a nuvem inicial
            pcm.save_to_file(
                filename=join(file_dir, "initial"),
                format="pcd"
                )
        
        # Aplica filtros na nuvem
        pcm.filter_by_distance(self._conf.distance)
        pcm.filter_statistical_outliers()

        # compute warping
        warping_list = []
        warping_list.append(pcm.compute_warping())
        warping_list.append(pcm.compute_warping2())
        warping_list.append((warping_list[0] + warping_list[1])/2)

        # caso seja para salvar, salva a nuvem final e escreve resultado da mediçao
        if self._conf.api_save:
            pcm.save_to_file(
                filename=join(file_dir, "final"),
                format="pcd"
                )
            self._write_measurement_result(join(file_dir, "Measurement.txt"), warping_list)
            
        # Open the visualization of the pcd
        if not self._conf.api_save:
            pcm.visualize(visualize_plane=True, warping_list=warping_list)
        
        # Finish the connection with the sensor after the measurement
        lidar.finish()
