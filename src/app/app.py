from config.config import Config
from lidar.lidar import LiDAR
from sys import exit
from time import sleep
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

class App:
    def __init__(self, conf:Config):
        self._conf = conf

    def _exit_program(self):
        print("Exiting the program...")
        exit(0) 

    def _process(self, scan_list:list[tuple], threshold:float):
        if threshold > 0:
            for i in range(len(scan_list)):
                # Extrair os valores de x e y da leitura atual
                x = np.array(scan_list[i][0])
                y = np.array(scan_list[i][1])

                # --- aplicar um threshold inicial --- #
                idxs = np.where(y > threshold)
                x = np.delete(x, idxs)
                y = np.delete(y, idxs)
                # ---

                # --- aplicar threshold LSC e LIC --- #
                mean = y.mean()
                devi = y.std()
                lcl = mean-2*devi
                ucl = mean+2*devi

                idxs = np.where(y < lcl)
                x = np.delete(x, idxs)
                y = np.delete(y, idxs)

                idxs = np.where(y > ucl)
                x = np.delete(x, idxs)
                y = np.delete(y, idxs)
                # ---

                # substitui a tupla inicial pela reduzida no processamento
                scan_list[i] = (x, y)

        self._plot(scan_list) # plotagem para vizualizar a núvem

        # scan_list é a núvem de pontos para continuar os processamentos
         
    def _plot(self, scan_list:list[tuple]):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        npoints = 0

        for z, scan in enumerate(scan_list):
            x = scan[0]
            y = scan[1]
            # Plotar os pontos 3D
            ax.scatter(x, y, z, c="g", s=1)

            npoints += len(x)
        
        # Configurações adicionais do gráfico
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Amostras')

        print(f"Leituras: {len(scan_list)}")
        print(f"Total de Pontos: {npoints}")

        # Exibir o gráfico
        plt.show()

    def start(self):
        lidar = LiDAR(self._conf.lidar_ip, self._conf.lidar_port, self._conf.min_angle, self._conf.max_angle)

        sleep(1)

        while True:
            if input("> ").strip() == "e":
                self._exit_program()
            else:
                scan_list = []
                start_time = datetime.now()
                
                while (datetime.now() - start_time).seconds <= 2:
                    lidar.get_cartesian_data()
                    scan_list.append(lidar.cartesian)
                    sleep(0.1) #um atraso para diminuir a quantidade de leituras
          
                self._process(scan_list, threshold=0)