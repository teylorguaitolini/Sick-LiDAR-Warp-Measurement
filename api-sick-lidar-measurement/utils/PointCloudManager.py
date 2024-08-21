import io
import base64
import open3d as o3d
import numpy as np
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

    def filter_by_distance(self, distance: int):
        try:
            # Aplicar o filtro de outliers
            self._filter_statistical_outliers()

            # carregar pontos após o filtro de outliers
            filtered_points = np.asarray(self.point_cloud.points)

            # Filtrar os pontos com base na distância especificada
            if distance > 0:
                filtered_points = filtered_points[filtered_points[:, 1] <= distance]
                logger.info(f"Points with Y coordinate greater than {distance} have been removed.")
            
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
    
    def WMUSS(self):
        """
        ### WMUSS (Warping Measurement for Upper Surface Scan)
        - Just measures the warping of the top slab in a stack.
        """
        try:
            points = np.asarray(self.point_cloud.points)

            y = points[:, 1]
            z = points[:, 2]

            # Calculate the mean and control limits
            mean_y = np.mean(y)
            std_y = np.std(y)
            ucl_y = mean_y + 3 * std_y
            lcl_y = mean_y - 3 * std_y

            # Filter the points within the control limits
            within_control_limits = (y >= lcl_y) & (y <= ucl_y)
            filtered_points = points[within_control_limits]
            filtered_y = y[within_control_limits]
            filtered_z = z[within_control_limits]

            # Calculate deviations of Y points from the mean
            deviations = filtered_y - mean_y
            max_deviation = float(np.max(np.abs(deviations)))
            max_deviation_point = filtered_points[np.argmax(np.abs(deviations))]

            # Plot the points, mean line, and max deviation point
            plt.figure(figsize=(10, 6))
            plt.scatter(filtered_z, filtered_y, s=1, c='blue', marker='.', label='Filtered Points')
            plt.axhline(mean_y, color='green', linestyle='-', linewidth=2, label='Mean')
            plt.axhline(ucl_y, color='red', linestyle='--', linewidth=2, label='UCL')
            plt.axhline(lcl_y, color='red', linestyle='--', linewidth=2, label='LCL')
            plt.scatter(max_deviation_point[2], max_deviation_point[1], color='red', s=50, label='Max Deviation')
            plt.xlabel('Z')
            plt.ylabel('Y')
            plt.grid(True)
            plt.legend()
            plt.title(f'Max Deviation (Warping): {(max_deviation*100):.3f} cm')

            # Save the image to a byte buffer
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)  # Go back to the beginning of the buffer
            plt.close()  # Close the figure to free memory
            img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')

            return max_deviation, img_str

        except Exception as e:
            raise Exception(f"Error in WMUSS: {e}")
    
    def WMLSS(self):
        """
        ### WMLSS (Warping Measurement for Lateral Stack Scan)
        - Method for lateral measurement.
        - Virtual Twine Method.
        """
        try:
            points = np.asarray(self.point_cloud.points)

            deviation = 0.0

            x = points[:, 0]
            z = points[:, 2]

            # Suponha que calculamos o desvio como a diferença média dos pontos z
            deviation = np.mean(x)  # Apenas um exemplo de cálculo

            # Gerar a imagem
            plt.figure(figsize=(10, 6))
            plt.scatter(z, x, c='blue', label='Points')
            plt.axhline(y=deviation, color='red', linestyle='--', label='Deviation')

            plt.title('Lateral Stack Scan - WMLSS')
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
