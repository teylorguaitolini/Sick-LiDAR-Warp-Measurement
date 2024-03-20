from src.config import Config
from src.lidar import LiDAR
from sys import exit
from time import sleep
from datetime import datetime
import numpy as np
import open3d as o3d
import matplotlib.pyplot as plt

class App:
    def __init__(self, conf:Config):
        self._conf = conf

    def start(self):
        if not self._conf.conf_sts:
            self.exit_program()

        lidar = LiDAR(self._conf.lidar_ip, self._conf.lidar_port, self._conf.min_angle, self._conf.max_angle)

        while True:
            lidar.connect()
            if lidar.lidar_sts:
                break
            sleep(0.5)

        sleep(1)

        while True:
            if input("> ").strip() == "e":
                self.exit_program()
            else:
                scan_list = []
                start_time = datetime.now()
                while (datetime.now() - start_time).seconds <= self._conf.scan_time:
                    lidar.get_data()
                    scan_list.append(lidar.cartesian)
                    sleep(0.1) #um atraso para diminuir a quantidade de leituras
                self.plot_3d(scan_list)
        
    def exit_program(self):
        print("Exiting the program...")
        exit(0)      

    
    def plot_3d(self, scan_list:list[tuple]):
        print(len(scan_list))
        print(len(scan_list[0][0]))

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        for z, scan in enumerate(scan_list):
            # Extrair os valores de x e y da leitura atual
            x = np.array(scan[0])
            y = np.array(scan[1])

            #aplicar um threshold
            idxs = np.where(y > 0.5)
            x = np.delete(x, idxs)
            y = np.delete(y, idxs)

            #aplicar threshold pela média
            mean = y.mean()
            idxs = np.where(y < mean)
            x = np.delete(x, idxs)
            y = np.delete(y, idxs)

            idxs = np.where(y > mean)
            x = np.delete(x, idxs)
            y = np.delete(y, idxs)
            
            # Plotar os pontos 3D
            ax.scatter(x, y, z, c="g", s=1)
        
        # Configurações adicionais do gráfico
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Amostras')

        # Exibir o gráfico
        plt.show()
