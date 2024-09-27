import io
import base64
import open3d as o3d
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from os import getcwd, makedirs
from os.path import join, exists
from utils.logger_config import logger

class PointCloudManager:
    def __init__(self):
        self.point_cloud = o3d.geometry.PointCloud()

        # --- Measurment results with Virtual Twine Algorithm --- #
        self._vt_warping = 0.0
        self._vt_warping_image = ""
        self._vt_lenght = 0.0
        self._vt_hight = 0.0
        self._vt_distance = 0.0
        # ---  --- #
    
    @property
    def vt_warping(self):
        return self._vt_warping
    
    @property
    def vt_warping_image(self):
        return self._vt_warping_image
    
    @property
    def vt_lenght(self):
        return self._vt_lenght
    
    @property
    def vt_hight(self):
        return self._vt_hight
    
    @property
    def vt_distance(self):
        return self._vt_distance

    def load_from_list(self, 
        pcd:list
    ):
        try:
            self._clear()
            self.point_cloud.points = o3d.utility.Vector3dVector(np.array(pcd))
            logger.info("Point cloud loaded from list")
        except Exception as e:
            raise Exception(f"Error in loading point cloud from list: {e}")
    
    def pcd2csv(self, 
        save: bool
    ):
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
        
    def encoder_to_real_Z_distance(self, 
        pulses_per_rev: int, 
        mm_per_rev:     float
    ):
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

            self.point_cloud.points = o3d.utility.Vector3dVector(points)
        except Exception as e:
            raise Exception(f"Error in encoder to real distance conversion: {e}")
    
    def data_adequacy(self, 
        mirror: bool = False
    ):
        """

        """
        try:
            points = np.asarray(self.point_cloud.points)

            x = points[:, 0]
            z = points[:, 2]

            # Shifting x to be fully positive, with a reference at 0
            min_x = np.min(x)
            if min_x < 0:
                x = x + np.abs(min_x)
            elif min_x > 0:
                x = x - min_x

            # Mirroring the z values since the LiDAR is inverted
            if mirror:
                z = z * -1
                min_z = np.min(z)
                z = z + np.abs(min_z)

            # Updating the point cloud with the adjusted values
            points[:, 0] = x
            points[:, 2] = z
            self.point_cloud.points = o3d.utility.Vector3dVector(points)
        except Exception as e:
            raise Exception(f"Error in data adequacy check: {e}")

    def filter_pcd(self,
        distance:   float = 0.0,
        target_std: float = 0.005, # Definindo o desvio padrão alvo como 0.005 metros (5 mm)
        max_num_i:  int   = 21
    ):
        """
        ### filter_by_distance

        :param distance: The distance between LiDAR and the object.
        """
        try:
            # --- Aplicar o pre filtro de distância (eixo Y) --- #
            self._distance_pre_filter(distance)
            # --- --- #
            
            # --- Aplicar o filtro de sigma para distancia (eixo Y) --- #
            sigmas = 3
            i_ref = int(max_num_i/sigmas)
            i = 1
            std = self._distance_sigma_filter(sigmas)
            while (std > target_std) and (i < max_num_i):
                if (i_ref < i <= (2*i_ref)):
                    sigmas = 2
                elif (i > (2*i_ref)):
                    sigmas = 1
                std = self._distance_sigma_filter(sigmas)
                i += 1
            #std = self._distance_sigma_filter(sigmas)
            logger.info(f"Final Std: {std}")
            # --- --- # 

            # --- Filtro de Comprimento (eixo Z) --- #
            self._length_filter()
            #--- --- #
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

            # Para o algoritmo do Barbante Virtual é feita a análise do perfil superior
            # Aqui os valores de X, Y e Z são trocados de lugar para facilitar a análise
            # Z -> X : Comprimento
            # X -> Y : Altura
            # Y -> Z : Distância / Profundidade
            self._virtualTwineAlgorithm(z, x, y)
        except Exception as e:
            raise Exception(f"Error in WMLSS: {e}")
    
    def _length_filter(self, 
        threshold: float = 0.01 # Definindo o threshold como 0.01 metros (1 cm)
    ):
        points = np.asarray(self.point_cloud.points)
        z = points[:, 2]

        # Ordenar os pontos com base no eixo Z
        sorted_indices = np.argsort(z)
        sorted_points = points[sorted_indices]
        sorted_z = z[sorted_indices]

        # Detectar buracos (quebra na continuidade)
        gaps = np.diff(sorted_z)
        large_gaps = np.where(gaps > threshold)[0]

        if len(large_gaps) == 0:
            # Se não houver buracos, usar o comprimento total
            z_min, z_max = sorted_z[0], sorted_z[-1]
        else:
            # Caso haja buracos, usar a primeira e a última borda válidas
            z_min = sorted_z[0]
            z_max = sorted_z[large_gaps[0]]

        # Filtrar pontos fora das bordas
        valid_indices = np.where((z >= z_min) & (z <= z_max))[0]
        filtered_points = points[valid_indices]

        # Atualizar os pontos na nuvem de pontos
        self.point_cloud.points = o3d.utility.Vector3dVector(filtered_points)
    
    def _distance_pre_filter(self, 
        distance: float = 0.0
    ):
        # carregar pontos após o filtro de outliers
        filtered_points = np.asarray(self.point_cloud.points)

        # Filtrar os pontos com base na distância especificada
        if distance > 0:
            filtered_points = filtered_points[filtered_points[:, 1] <= distance]
        
        # Atualizar os pontos na nuvem de pontos
        self.point_cloud.points = o3d.utility.Vector3dVector(filtered_points)
    
    def _distance_sigma_filter(self, 
        sigmas: int = 3
    ):
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
    
    def _virtualTwineAlgorithm(self, 
        x: np.ndarray, 
        y: np.ndarray, 
        z: np.ndarray
    ):
        """
        ### virtualTwineAlgorithm
        Algorithm to calculate the warping by identifying the upper edge of a profile.
        
        :param x: np.ndarray, x-coordinates of the profile points - Length
        :param y: np.ndarray, y-coordinates of the profile points - Height
        :param z: np.ndarray, z-coordinates of the profile points - Distance / Depth
        
        :return: warping (float), a measure of the warping along the upper edge
        """
        upper_edge = self._upper_edge_finder(x, y)
        
        # Calcular o "warping" como a diferença entre o maior e o menor valor de y na borda superior
        max_y = np.max(upper_edge[1])
        min_y = np.min(upper_edge[1])

        self._vt_warping = max_y - min_y
        self._vt_lenght = np.max(x) - np.min(x)
        self._vt_hight = np.max(y) - np.min(y)
        self._vt_distance = np.mean(z)
        self._vt_warping_image = self._virtualTwinePloter(x, y, upper_edge[0], upper_edge[1], max_y, min_y)
    
    def _upper_edge_finder(self, 
        x: np.ndarray, 
        y: np.ndarray,
        diff_threshold: float = 0.01  # Desired threshold in meters (e.g., 10 mm = 0.01 meters)
    ):
        """
        ### upper_edge_finder
        Algorithm to find the upper edge of a profile, remove outliers, and ensure points are processed in order of increasing x.

        :param x: np.ndarray, x-coordinates of the profile points
        :param y: np.ndarray, y-coordinates of the profile points
        :param diff_threshold: float, the absolute difference threshold (e.g., 10 mm = 0.01 meters)

        :return: filtered_x (np.ndarray), unique x-coordinates of the profile points with outliers removed
        :return: filtered_y (np.ndarray), y-coordinates of the upper edge with outliers removed
        """
        # Sort points by x-coordinate
        sorted_indices = np.argsort(x)
        x = x[sorted_indices]
        y = y[sorted_indices]

        # Unique x values
        unique_x = np.unique(x)
        upper_edge_y = np.full_like(unique_x, -np.inf, dtype=float)

        # Identify the upper edge by selecting the maximum y for each unique x
        for i, x_val in enumerate(unique_x):
            indices = np.where(x == x_val)[0]
            upper_edge_y[i] = np.max(y[indices])

        # Remove outliers from the upper edge using the 3-standard-deviation rule
        mean_y = np.mean(upper_edge_y)
        std_y = np.std(upper_edge_y)

        # Define the threshold for outliers
        threshold_lower = mean_y - 3 * std_y
        threshold_upper = mean_y + 3 * std_y

        # Find indices of outliers
        outliers = np.where((upper_edge_y < threshold_lower) | (upper_edge_y > threshold_upper))

        # Remove the outliers from both upper_edge_y and unique_x
        upper_edge_y = np.delete(upper_edge_y, outliers)
        unique_x = np.delete(unique_x, outliers)

        # Calculate the differences between consecutive y values
        diff_y = np.diff(upper_edge_y)

        # Dynamically calculate diff_threshold_factor based on the median difference
        median_diff = np.median(np.abs(diff_y))

        if median_diff > diff_threshold:
            median_diff = diff_threshold

        # Find indices where the difference between consecutive y values exceeds the threshold
        #large_diff_indices = np.where(np.abs(diff_y) > diff_threshold)[0]
        large_diff_indices = np.where(np.abs(diff_y) > median_diff)[0]

        # Since np.diff() reduces the array size by 1, we need to remove both the current and next point
        # Remove the corresponding points from both upper_edge_y and unique_x
        filtered_y = np.delete(upper_edge_y, large_diff_indices + 1)  # Remove the next point
        filtered_x = np.delete(unique_x, large_diff_indices + 1)

        return filtered_x, filtered_y
    
    def _virtualTwinePloter(self,
        x:            np.ndarray,
        y:            np.ndarray,
        upper_edge_x: np.ndarray,
        upper_edge_y: np.ndarray,
        max_y:        float,
        min_y:        float
    ):
        plt.figure(figsize=(16, 9))  # "Tela cheia"
        plt.scatter(x, y, s=2, label="Perfil original", c="lightblue")
        # plt.autoscale(tight=True)
        n_ticks = 10
        plt.xticks(np.linspace(min(x), max(x), n_ticks))
        plt.yticks(np.linspace(min(y), max(y), n_ticks))
        plt.plot(upper_edge_x, upper_edge_y, 'r-', label="Borda superior")

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

        b64_image = base64.b64encode(buffer.getvalue()).decode('utf-8')

        return b64_image

    def _filter_statistical_outliers(self, 
        nb_neighbors:   int = 20, 
        std_ratio:      float = 2.0
    ):
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
