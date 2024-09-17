import io
import base64
import open3d as o3d
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from math import ceil
from datetime import datetime
from os import getcwd, makedirs
from os.path import join, exists
from utils.logger_config import logger

class PointCloudManager:
    def __init__(self):
        self.point_cloud = o3d.geometry.PointCloud()

        # Measurment results with Virtual Twine Algorithm
        self._vt_warping = 0.0
        self._vt_warping_image = None
        self._vt_lenght = 0.0
        self._vt_hight = 0.0
        self._vt_distance = 0.0

    def load_from_list(self, pcd:list):
        try:
            self._clear()
            self.point_cloud.points = o3d.utility.Vector3dVector(np.array(pcd))
            logger.info("Point cloud loaded from list")
        except Exception as e:
            raise Exception(f"Error in loading point cloud from list: {e}")
    
    def pcd2csv(self, save: bool):
        try:
            if save:
                points = np.asarray(self.point_cloud.points)
                df = pd.DataFrame(points, columns=['x', 'y', 'z'])
                
                DIR = join(getcwd(), "PCDs")
                if not exists(DIR):
                    makedirs(DIR)
                
                filename = datetime.now().strftime('%Y%m%d_%H%M%S') + ".csv"

                df.to_csv(join(DIR, filename), index=False)
        except Exception as e:
            raise Exception(f"Error in generating JSON PCD: {e}")
        
    def encoder_to_real_Z_distance(self, pulses_per_rev: int, mm_per_rev: float):
        """
        Converts encoder numbers to real distance in meters.

        :param: pulses_per_rev (int): The number of pulses per revolution of the encoder.
        :param: mm_per_rev (float): The distance in millimeters covered by one revolution of the encoder.
        """
        try:
            points = np.asarray(self.point_cloud.points)

            z = points[:, 2]

            # Converting encoder number to real distance in meters
            mm_per_pulse = (mm_per_rev / pulses_per_rev) # mm per tick (pulse)
            mm_per_pulse = mm_per_pulse / 1000  # in meters
            z = z * mm_per_pulse

            # Updating the point cloud with the adjusted values
            points[:, 2] = z

            # Removing points with Z values greater than 20 meters
            # this is due the encoder overflow
            # points = points[points[:, 2] >= -20000]

            self.point_cloud.points = o3d.utility.Vector3dVector(points)
        except Exception as e:
            raise Exception(f"Error in encoder to real distance conversion: {e}")
    
    def data_adequacy(self):
        """

        """
        try:
            points = np.asarray(self.point_cloud.points)

            x = points[:, 0]
            # z = points[:, 2]

            # Shifting x to be fully positive, with a reference at 0
            minv = np.min(x)
            if minv < 0:
                x = x + np.abs(minv)
            elif minv > 0:
                x = x - minv

            # Shifting z to be fully positive, with a reference at 0, if moving to the left
            # minv = np.min(z)
            # if minv < 0:
            #     z = z + np.abs(minv)

            # Updating the point cloud with the adjusted values
            points[:, 0] = x
            # points[:, 2] = z
            self.point_cloud.points = o3d.utility.Vector3dVector(points)
        except Exception as e:
            raise Exception(f"Error in data adequacy check: {e}")

    def filter_by_Y_distance(self, distance: float, num_iterations: int):
        """
        ### filter_by_distance

        :param distance: The distance between LiDAR and the object.
        """
        try:
            # carregar pontos após o filtro de outliers
            filtered_points = np.asarray(self.point_cloud.points)

            # Filtrar os pontos com base na distância especificada
            if distance > 0:
                filtered_points = filtered_points[filtered_points[:, 1] <= distance]
            
            # Atualizar os pontos na nuvem de pontos
            self.point_cloud.points = o3d.utility.Vector3dVector(filtered_points)
            
            # Aplicar o filtro de sigma
            if num_iterations > 0:
                for _ in range(num_iterations):
                    self._sigma_filter()
            else:
                i = 0
                std = self._sigma_filter()
                while (std > 0.01) and (i <= 30):
                    std = self._sigma_filter()
                    i += 1
                logger.info(f"Final Std: {std}")
            
        except Exception as e:
            raise Exception(f"Error in filtering by distance: {e}")
    
    def virtualTwine(self):
        """
        ### virtualTwine
        - Warping Measurement for Lateral Stack Scan.
        - Virtual Twine Method.
        """
        try:
            points = np.asarray(self.point_cloud.points)

            x = points[:, 0]
            y = points[:, 1]
            z = points[:, 2]

            # here comes the algorithm to calculate the deviation
            self._virtualTwineAlgorithm(z, x)

            self._vt_lenght = np.max(z) - np.min(z)
            self._vt_hight = np.max(x) - np.min(x)
            self._vt_distance = np.mean(y)
        except Exception as e:
            raise Exception(f"Error in WMLSS: {e}")

    def _sigma_filter(self, sigmas: int = 2):
        # Aplicar o filtro de outliers
        self._filter_statistical_outliers()

        # carregar pontos após o filtro de outliers
        filtered_points = np.asarray(self.point_cloud.points)

        # Calcular a moda das coordenadas Y
        y_coordinates = np.round(filtered_points[:, 1], 2)
        unique_vals, inverse = np.unique(y_coordinates, return_inverse=True)
        mode_index = np.bincount(inverse).argmax()
        mode_y = unique_vals[mode_index]

        # Calcular os limites de controle
        std = np.std(y_coordinates)
        ucl = mode_y + sigmas * std
        lcl = mode_y - sigmas * std
        logger.info(f"Mode of Y coordinates: {mode_y}, Std: {std} UCL: {ucl}, LCL: {lcl}")

        # Aplicar os filtros de controle
        filtered_points = filtered_points[(y_coordinates <= ucl) & (y_coordinates >= lcl)]

        # Calcular o desvio padrão atualizado
        y_coordinates = np.round(filtered_points[:, 1], 2)
        std = np.std(y_coordinates)

        # Atualizar os pontos na nuvem de pontos
        self.point_cloud.points = o3d.utility.Vector3dVector(filtered_points)

        return std
    
    def _virtualTwineAlgorithm(self, x: np.ndarray, y: np.ndarray):
        """
        ### virtualTwineAlgorithm
        Algorithm to calculate the warping by identifying the upper edge of a profile.
        
        :param x: np.ndarray, x-coordinates of the profile points
        :param y: np.ndarray, y-coordinates of the profile points
        
        :return: warping (float), a measure of the warping along the upper edge
        """

        # Inicializa a borda superior com -inf para cada valor único de x
        unique_x = np.unique(x)
        upper_edge_y = np.full_like(unique_x, -np.inf, dtype=float)

        # Para cada x, encontre o maior y correspondente
        for i, x_val in enumerate(unique_x):
            indices = np.where(x == x_val)[0]
            upper_edge_y[i] = np.max(y[indices])
        
        plt.figure(figsize=(16, 9))  # "Tela cheia"
        plt.scatter(x, y, s=2, label="Perfil original", c="lightblue")
        # plt.autoscale(tight=True)
        n_ticks = 10
        plt.xticks(np.linspace(min(x), max(x), n_ticks))
        plt.yticks(np.linspace(min(y), max(y), n_ticks))
        plt.plot(unique_x, upper_edge_y, 'r-', label="Borda superior")
        
        # Calcular o "warping" como a diferença entre o maior e o menor valor de y na borda superior
        max_y = np.max(upper_edge_y)
        min_y = np.min(upper_edge_y)
        self._vt_warping = max_y - min_y

        plt.axhline(y=max_y, color='orange', linestyle='-', label='Máx. y (Borda superior)')
        plt.axhline(y=min_y, color='darkgreen', linestyle='-', label='Mín. y (Borda superior)')

        plt.title('Medição do Empeno: Barbante Virtual')
        plt.ylabel('Altura [m]')
        plt.xlabel('Comprimento [m]')
        plt.legend()
        plt.grid(True)

        # Salvar a imagem como base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        buffer.seek(0)
        plt.close()
        self._vt_warping_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    def _filter_statistical_outliers(self, nb_neighbors=20, std_ratio=2.0):
        try:
            cl, ind = self.point_cloud.remove_statistical_outlier(nb_neighbors=nb_neighbors, std_ratio=std_ratio)
            self.point_cloud = self.point_cloud.select_by_index(ind)
            logger.info("Statistical outlier filtering applied to the point cloud.")
        except Exception as e:
            raise Exception(f"Error in statistical outlier filtering: {e}")
    
    def _clear(self):
        try:
            if self.point_cloud.has_points():
                self.point_cloud.clear()
        except Exception as e:
            raise Exception(f"Error in clearing the point cloud: {e}")
