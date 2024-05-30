import open3d as o3d
import numpy as np

class PointCloudManager:
    def __init__(self):
        self.point_cloud = o3d.geometry.PointCloud()
    
    def _clear(self):
        if self.point_cloud.has_points():
            self.point_cloud.clear()
        print("Point cloud cleared.")

    def load_from_list(self, scans:list):
        self._clear()
        self.point_cloud.points = o3d.utility.Vector3dVector(np.array(scans))
        print("Point cloud loaded from list")

    def load_from_file(self, filename):
        self._clear()
        self.point_cloud = o3d.io.read_point_cloud(filename)
        print(f"Point cloud loaded from {filename}")
    
    def save_to_file(self, filename, format='pcd'):
        if format == 'pcd':
            o3d.io.write_point_cloud(filename, self.point_cloud)
        elif format == 'ply':
            o3d.io.write_point_cloud(filename, self.point_cloud)
        else:
            raise ValueError("Unsupported file format. Use 'pcd' or 'ply'.")
        print(f"Point cloud saved to {filename}")
    
    def visualize(self):
        o3d.visualization.draw_geometries([self.point_cloud])
        print(self.point_cloud)
        print("Point cloud visualized.")
    
    def filter_by_distance(self, distance):
        # Filtra os pontos da nuvem onde a coordenada Y é maior que a distância especificada
        points = np.asarray(self.point_cloud.points)
        filtered_points = points[points[:, 1] <= distance]
        self.point_cloud.points = o3d.utility.Vector3dVector(filtered_points)
        print(f"Points with Y coordinate greater than {distance} have been removed.")
    
    def filter_statistical_outliers(self, nb_neighbors=20, std_ratio=2.0):
        cl, ind = self.point_cloud.remove_statistical_outlier(nb_neighbors=nb_neighbors, std_ratio=std_ratio)
        self.point_cloud = self.point_cloud.select_by_index(ind)
        print("Statistical outlier filtering applied to the point cloud.")
    
    def downsample(self, voxel_size):
        self.point_cloud = self.point_cloud.voxel_down_sample(voxel_size=voxel_size)
        print(f"Point cloud downsampled with voxel size {voxel_size}.")
    
    def compute_warping(self):
        """
        - Ajuste de um Plano:
        
        Utiliza o método segment_plane do Open3D para ajustar um plano aos pontos da nuvem.
        O plano é representado pela equação ax + by + cz + d = 0.
        
        - Cálculo das Distâncias:
        
        Calcula a distância de cada ponto ao plano ajustado usando a fórmula da distância ponto-plano.
        distances = np.abs(a * x + b * y + c * z + d) / sqrt(a^2 + b^2 + c^2).
        
        - Análise de Empenamento:
        
        Determina o valor de empenamento como a máxima distância calculada dos pontos ao plano.
        O valor máximo indica a maior deformação da placa em relação ao plano ideal.
        """
        # Fit a plane to the point cloud
        plane_model, inliers = self.point_cloud.segment_plane(distance_threshold=0.01,
                                                              ransac_n=3,
                                                              num_iterations=1000)
        [a, b, c, d] = plane_model
        print(f"Plane equation: {a}x + {b}y + {c}z + {d} = 0")

        # Calculate the distance of each point to the plane
        points = np.asarray(self.point_cloud.points)
        distances = np.abs(a * points[:, 0] + b * points[:, 1] + c * points[:, 2] + d) / np.sqrt(a**2 + b**2 + c**2)

        # Compute warping as the max distance from the plane
        warping_value = np.max(distances)
        print(f"Maximum warping distance: {warping_value}")

        return warping_value
