from src.config import Config
from src.lidar import LiDAR
from sys import exit
from time import sleep
import numpy as np
import open3d as o3d

class App:
    def __init__(self, conf:Config):
        self.__conf = conf

    def start(self):
        if not self.__conf.conf_sts:
            self.exit_program()

        lidar = LiDAR(self.__conf.lidar_ip, self.__conf.lidar_port)

        while True:
            lidar.connect()

            if lidar.lidar_sts:
                break
            else:
                sleep(0.5)

        while True:
            lidar.get_data()
            self.plot_3d(lidar.cartesian)
            if input("> ").strip() == "exit":
                self.exit_program()
            else:
                continue
            #sleep(1)

        
    def exit_program(self):
        print("Exiting the program...")
        exit(0)
    
    def plot_3d(self, cartesian):
        x, y = cartesian
        print(x)
        print(y)

        