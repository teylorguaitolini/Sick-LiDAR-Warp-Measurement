import inspect
import open3d as o3d
import numpy as np
import matplotlib.pyplot as plt
from os.path import join, exists
from os import makedirs
from datetime import datetime
from config.logger_config import logger
#from scipy.signal import find_peaks
from sklearn.linear_model import LinearRegression

class PointCloudManager:
    def __init__(self):
        self.point_cloud = o3d.geometry.PointCloud()
        self.plane_model = []
        self.warping_results_list = []

    def load_from_list(self, pcd:list):
        try:
            self._clear()
            self.point_cloud.points = o3d.utility.Vector3dVector(np.array(pcd))
            logger.info("Point cloud loaded from list")
        except Exception as e:
            raise e

    def load_from_file(self, filename):
        try:
            self._clear()
            self.point_cloud = o3d.io.read_point_cloud(filename)
            logger.info(f"Point cloud loaded from {filename}")
        except Exception as e:
            raise e
    
    def save_to_file(self, filename:str, format='pcd'):
        try:
            if format == 'pcd' or format == 'ply':
                o3d.io.write_point_cloud(filename+"."+format, self.point_cloud)
            else:
                raise ValueError("Unsupported file format. Use 'pcd' or 'ply'.")
            logger.info(f"Point cloud saved to {filename}")
        except Exception as e:
            raise e

    def filter_by_distance(self, distance:int):
        try:
            points = np.asarray(self.point_cloud.points)

            if (distance>0):
                # Filtra os pontos da nuvem onde a coordenada Y é maior que a distância especificada
                filtered_points = points[points[:, 1] <= distance]
                self.point_cloud.points = o3d.utility.Vector3dVector(filtered_points)
                logger.info(f"Points with Y coordinate greater than {distance} have been removed.")

        except Exception as e:
            raise e
    
    def filter_statistical_outliers(self, nb_neighbors=20, std_ratio=2.0):
        try:
            cl, ind = self.point_cloud.remove_statistical_outlier(nb_neighbors=nb_neighbors, std_ratio=std_ratio)
            self.point_cloud = self.point_cloud.select_by_index(ind)
            logger.info("Statistical outlier filtering applied to the point cloud.")
        except Exception as e:
            raise e
    
    def WMUSS(self, save: bool, DIR: str):
        """
        ### WMUSS (Warping Measurement for Upper Surface Scan)
        - Just measures the warping of the top slab in a stack.
        """
        try:
            # create the directory to save the results
            file_dir = ""
            if save:
                file_dir = join(DIR, "Measurements", str(datetime.now().strftime('%Y%m%d_%H%M%S')))
                if not exists(file_dir):
                    makedirs(file_dir)
                # save the point cloud
                self.save_to_file(join(file_dir, "Measurement"))

            points = np.asarray(self.point_cloud.points)

            y = points[:, 1]
            z = points[:, 2]

            # Calcular a média e os limites de controle
            mean_y = np.mean(y)
            std_y = np.std(y)
            ucl_y = mean_y + 3 * std_y
            lcl_y = mean_y - 3 * std_y

            # Filtrar os pontos dentro dos limites de controle
            within_control_limits = (y >= lcl_y) & (y <= ucl_y)
            filtered_points = points[within_control_limits]
            filtered_y = y[within_control_limits]
            filtered_z = z[within_control_limits]

            # Regressão linear para Y em relação a Z com pontos filtrados
            z_reshaped = filtered_z.reshape(-1, 1)
            reg = LinearRegression().fit(z_reshaped, filtered_y)
            y_pred = reg.predict(z_reshaped)

            # Calcular desvios dos pontos Y em relação à linha de regressão
            deviations = filtered_y - y_pred
            max_deviation = float(np.max(np.abs(deviations)))
            max_deviation_point = filtered_points[np.argmax(np.abs(deviations))]

            # Plotar os pontos, a linha de regressão e o ponto de maior desvio
            plt.figure(figsize=(10, 6))
            plt.scatter(filtered_z, filtered_y, s=1, c='blue', marker='.', label='Filtered Points')
            plt.plot(filtered_z, y_pred, color='orange', label='Linear Regression')
            plt.axhline(mean_y, color='green', linestyle='-', linewidth=2, label='Mean')
            plt.axhline(ucl_y, color='red', linestyle='--', linewidth=2, label='UCL')
            plt.axhline(lcl_y, color='red', linestyle='--', linewidth=2, label='LCL')
            plt.scatter(max_deviation_point[2], max_deviation_point[1], color='red', s=50, label='Max Deviation')
            plt.xlabel('Z')
            plt.ylabel('Y')
            plt.grid(True)
            plt.legend()
            plt.title(f'Max Deviation (Warping): {(max_deviation*100):.2f} cm')

            if save:
                # Saves the PNG
                plt.savefig(join(file_dir, "Measurement.png"))

                # Saves the result in a txt file
                self._write_measurement_results(join(file_dir, "Measurement.txt"), max_deviation)
            else:
                plt.show()
                # Open the visualization of the pcd
                self._visualize3D()

            return max_deviation
        except Exception as e:
            raise e

    
    def WMLSS(self, save:bool, DIR:str):
        """
        ### WMLSS (Warping Measurement for Lateral Stack Scan)
        - Method for lateral measureent.
        - Virtual Twine Method.
        """
        try:
            # create the directory to save the results
            file_dir = ""
            if save:
                file_dir = join(DIR, "Measurements", str(datetime.now().strftime('%Y%m%d_%H%M%S')))
                if not exists(file_dir):
                    makedirs(file_dir)
                # save the point cloud
                self.save_to_file(join(file_dir, "Measurement"))


            if save:
                pass
            else:
                # Open the visualization of the pcd
                self._visualize3D()
        except Exception as e:
            raise e

    def _visualize3D(self):
        """
        ### visualize3D
        - Visualizes the point cloud.
        """
        try:
            self.point_cloud.paint_uniform_color([0, 0.5, 1]) # blue
            o3d.visualization.draw_geometries([self.point_cloud])
        except Exception as e:
            raise e
    
    def _clear(self):
        try:
            if self.point_cloud.has_points():
                self.point_cloud.clear()
        except Exception as e:
            raise e
        
    def _write_measurement_results(self, filename:str, warping_result:float):
        try:
            with open(filename, 'a') as file:
                file.write(f"Measured Warping by Method {inspect.stack()[1][3]}: {(warping_result*100):.2f} cm\n")
                logger.info(f"Measurement Result was saved successfully in {filename}.")
        except Exception as e:
            logger.error(f"Ocorreu um erro em write_measurement_result(): {e}.")
