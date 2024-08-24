import io
import base64
import open3d as o3d
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from utils.logger_config import logger

class PointCloudManager:
    def __init__(self):
        self.point_cloud = o3d.geometry.PointCloud()

    def load_from_list(self, pcd:list):
        try:
            self._clear()
            self.point_cloud.points = o3d.utility.Vector3dVector(np.array(pcd))
            logger.info("Point cloud loaded from list")
        except Exception as e:
            raise Exception(f"Error in loading point cloud from list: {e}")
    
    def save_to_file(self, filename:str, format='pcd'):
        try:
            if format == 'pcd' or format == 'ply':
                o3d.io.write_point_cloud(filename+"."+format, self.point_cloud)
            else:
                raise ValueError("Unsupported file format. Use 'pcd' or 'ply'.")
            logger.info(f"Point cloud saved to {filename}")
        except Exception as e:
            raise Exception(f"Error in saving point cloud to file: {e}")
    
    def pcd_json(self):
        try:
            points = np.asarray(self.point_cloud.points)
            df = pd.DataFrame(points, columns=['x', 'y', 'z'])
            json_data = df.to_json(orient='records')

            return json_data
        except Exception as e:
            raise Exception(f"Error in generating JSON PCD: {e}")
        
    def encoder_to_real_distance(self, pulses_per_rev: float, mm_per_rev: float):
        """
        Converts encoder numbers to real distance in meters.

        :param: pulses_per_rev (float): The number of pulses per revolution of the encoder.
        :param: mm_per_rev (float): The distance in millimeters covered by one revolution of the encoder.
        """
        try:
            points = np.asarray(self.point_cloud.points)

            z = points[:, 2]

            # Converting encoder number to real distance in meters
            ratio = (mm_per_rev / pulses_per_rev) # mm per tick (pulse)
            z = z * (ratio / 1000)

            # Updating the point cloud with the adjusted values
            points[:, 2] = z
            self.point_cloud.points = o3d.utility.Vector3dVector(points)
        except Exception as e:
            raise Exception(f"Error in encoder to real distance conversion: {e}")
    
    def data_adequacy(self):
        """

        """
        try:
            points = np.asarray(self.point_cloud.points)

            x = points[:, 0]
            z = points[:, 2]

            # Shifting x to be fully positive, with a reference at 0
            minv = np.min(x)
            if minv < 0:
                x = x + np.abs(minv)

            # Shifting z to be fully positive, with a reference at 0, if moving to the left
            minv = np.min(z)
            if minv < 0:
                z = z + np.abs(minv)

            # Updating the point cloud with the adjusted values
            points[:, 0] = x
            points[:, 2] = z
            self.point_cloud.points = o3d.utility.Vector3dVector(points)
        except Exception as e:
            raise Exception(f"Error in data adequacy check: {e}")


    def filter_by_distance(self, distance: int):
        """
        ### filter_by_distance

        :param distance: The distance between LiDAR and the object.
        """
        try:
            # Aplicar o filtro de outliers
            self._filter_statistical_outliers()

            # carregar pontos após o filtro de outliers
            filtered_points = np.asarray(self.point_cloud.points)

            # Filtrar os pontos com base na distância especificada
            if distance > 0:
                filtered_points = filtered_points[filtered_points[:, 1] <= distance]
            
            # Calcular a moda das coordenadas Y
            y_coordinates = np.round(filtered_points[:, 1], 2)
            unique_vals, inverse = np.unique(y_coordinates, return_inverse=True)
            mode_index = np.bincount(inverse).argmax()
            mode_y = unique_vals[mode_index]

            # Calcular os limites de controle
            std = np.std(y_coordinates)
            ucl = mode_y + 3 * std
            lcl = mode_y - 3 * std
            logger.info(f"Mode of Y coordinates: {mode_y}, UCL: {ucl}, LCL: {lcl}")

            # Aplicar os filtros de controle
            filtered_points = filtered_points[(y_coordinates <= ucl) & (y_coordinates >= lcl)]

            # Atualizar os pontos na nuvem de pontos
            self.point_cloud.points = o3d.utility.Vector3dVector(filtered_points)
            
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
            z = points[:, 2]

            # here comes the algorithm to calculate the deviation
            deviation = self._virtualTwineAlgorithm(x, z)

            # Gerar a imagem
            plt.figure(figsize=(10, 6))
            plt.scatter(z, x, c='blue', label='Points')
            plt.axhline(y=deviation, color='red', linestyle='--', label='Deviation')

            # Definir limites dos eixos
            plt.autoscale(tight=True)
            n_ticks = 10
            plt.xticks(np.linspace(min(z), max(z), n_ticks))
            plt.yticks(np.linspace(min(x), max(x), n_ticks))

            plt.title('Warping Measurement by Virtual Twine Method')
            plt.xlabel('Z axis')
            plt.ylabel('X axis')
            plt.legend()
            plt.grid(True)
            
            # Save the image to a byte buffer
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)  # Go back to the beginning of the buffer
            plt.close()  # Close the figure to free memory
            img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')

            return deviation, img_str
        except Exception as e:
            raise Exception(f"Error in WMLSS: {e}")
    
    def _virtualTwineAlgorithm(self, x: np.ndarray, z: np.ndarray):
        """
        ### virtualTwineAlgorithm
        algorithm to calculate the warping
        """
        deviation = 0.0
        return deviation
    
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
