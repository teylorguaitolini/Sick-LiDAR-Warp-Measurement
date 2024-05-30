import keyboard
from time import sleep
from config import Config
from sick.LMS4000 import LMS4000
from app import PointCloudManager

class App:
    def __init__(self, conf:Config):
        # --- Dados do Arquivo de configuração --- #
        self._conf = conf
        # --- Objeto que abstrai o sensor LiDAR X --- #
        self._lidar = LMS4000(self._conf.lidar_ip, self._conf.lidar_port, self._conf.start_angle, self._conf.stop_angle)
        # --- Objeto PointCloudManager --- #
        self._pcm = PointCloudManager()
    
    def flag(self):
        """
        Método para capturar o sinal de início da medição
        """
        print("Aguardando sinal para iniciar a rotina...")
        if keyboard.is_pressed('1'):
            print("Iniciando aquisição de dados...")
            return True
        else:
            return False
    
    def measurement_rotine(self):
        """
        Método principal da rotina de medição
        """
        scans = self._lidar.data_acquisition_routine()
        # plota a nuvem de pontos
        self._pcm.load_from_list(scans)
        self._pcm.filter_by_distance(self._conf.distance)
        self._pcm.filter_statistical_outliers()
        self._pcm.compute_warping()
        self._pcm.visualize()
    
    def end(self):
        """
        Rotina a ser executada sempre que o programa for encerrado
        """
        print("Encerrando programa...")
        self._lidar.finish()

    def start(self):
        while True:
            if self.flag():
                self.measurement_rotine()
            sleep(1)
