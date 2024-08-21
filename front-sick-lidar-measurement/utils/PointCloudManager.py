import open3d as o3d
import numpy as np

class PointCloudManager:
    def __init__(self):
        self.point_cloud = o3d.geometry.PointCloud()

    def load_from_file(self, filename):
        try:
            self._clear()
            self.point_cloud = o3d.io.read_point_cloud(filename)
        except Exception as e:
            raise Exception(f"Error loading point cloud from file: {e}")
    
    def visualize3D(self):
        """
        ### visualize3D
        - Visualizes the point cloud with axes and a grid.
        """
        try:
            # Pinta a nuvem de pontos
            self.point_cloud.paint_uniform_color([0, 0.5, 1])
            
            # Cria os eixos (frame de coordenadas)
            axes = o3d.geometry.TriangleMesh.create_coordinate_frame(size=1, origin=[0, 0, 0])
            
            # Cria a grade (10x10) em torno do eixo XZ
            grid_lines = self._create_grid(size=10, n=10)

            # Visualiza a nuvem de pontos com os eixos e a grade
            o3d.visualization.draw_geometries([self.point_cloud, axes, grid_lines])
        except Exception as e:
            raise e

    def _clear(self):
        try:
            if self.point_cloud.has_points():
                self.point_cloud.clear()
        except Exception as e:
            raise Exception(f"Error clearing point cloud: {e}")

    def _create_grid(self, size=10, n=10):
        """
        Cria uma grade (grid) no plano XZ.

        :param size: Tamanho da grid.
        :param n: Número de divisões na grid.
        :return: Uma geometria LineSet que representa a grade.
        """
        lines = []
        points = []

        for i in range(n + 1):
            x = i * size / n - size / 2
            points.append([x, 0, -size / 2])
            points.append([x, 0, size / 2])
            points.append([-size / 2, 0, x])
            points.append([size / 2, 0, x])
            lines.append([i * 4, i * 4 + 1])
            lines.append([i * 4 + 2, i * 4 + 3])

        line_set = o3d.geometry.LineSet(
            points=o3d.utility.Vector3dVector(points),
            lines=o3d.utility.Vector2iVector(lines),
        )
        return line_set
