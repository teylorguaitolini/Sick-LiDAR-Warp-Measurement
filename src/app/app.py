import keyboard
import open3d as o3d
import numpy as np
from time import sleep
from config.config import Config
from sick.LMS4000.lms4000 import LMS4000

class App:
    def __init__(self, conf:Config):
        # --- Dados do Arquivo de configuração --- #
        self._conf = conf
        # --- Objeto que abstrai o sensor LiDAR X --- #
        self._lidar = LMS4000(self._conf.lidar_ip, self._conf.lidar_port, self._conf.min_angle, self._conf.max_angle)
    
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

        pc = o3d.geometry.PointCloud()
        pc.points = o3d.utility.Vector3dVector(np.array(scans))
        o3d.visualization.draw_geometries([pc])
        print(pc)
    
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
