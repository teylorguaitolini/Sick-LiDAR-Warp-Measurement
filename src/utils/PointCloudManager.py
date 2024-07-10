import open3d as o3d
import numpy as np
import pyvista as pv

class PointCloudManager:
    def __init__(self):
        self.point_cloud = o3d.geometry.PointCloud()
        self.plane_model = []
    
    def _clear(self):
        if self.point_cloud.has_points():
            self.point_cloud.clear()
        print("Point cloud cleared.")

    def load_from_list(self, pcd:list):
        self._clear()
        self.point_cloud.points = o3d.utility.Vector3dVector(np.array(pcd))
        print("Point cloud loaded from list")

    def load_from_file(self, filename):
        self._clear()
        self.point_cloud = o3d.io.read_point_cloud(filename)
        print(f"Point cloud loaded from {filename}")
    
    def save_to_file(self, filename:str, format='pcd'):
        if format == 'pcd' or format == 'ply':
            o3d.io.write_point_cloud(filename+"."+format, self.point_cloud)
        else:
            raise ValueError("Unsupported file format. Use 'pcd' or 'ply'.")
        print(f"Point cloud saved to {filename}")

    def filter_by_distance(self, distance:int):
        if (distance>0):
            # Filtra os pontos da nuvem onde a coordenada Y é maior que a distância especificada
            points = np.asarray(self.point_cloud.points)
            filtered_points = points[points[:, 1] <= distance]
            self.point_cloud.points = o3d.utility.Vector3dVector(filtered_points)
            print(f"Points with Y coordinate greater than {distance} have been removed.")
    
    def filter_statistical_outliers(self, nb_neighbors=20, std_ratio=2.0):
        cl, ind = self.point_cloud.remove_statistical_outlier(nb_neighbors=nb_neighbors, std_ratio=std_ratio)
        self.point_cloud = self.point_cloud.select_by_index(ind)
        print("Statistical outlier filtering applied to the point cloud.")
    
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
        self.plane_model, inliers = self.point_cloud.segment_plane(distance_threshold=0.01,
                                                                ransac_n=3,
                                                                num_iterations=1000,
                                                                probability=1)
        
        [a, b, c, d] = self.plane_model
        plane_equation = f"Plane equation: {a:.2f}x + {b:.2f}y + {c:.2f}z + {d:.2f} = 0"

        # Calculate the distance of each point to the plane
        points = np.asarray(self.point_cloud.points)
        distances = np.abs(a * points[:, 0] + b * points[:, 1] + c * points[:, 2] + d) / np.sqrt(a**2 + b**2 + c**2)

        # Compute warping as the max distance from the plane
        warping_value = float(np.max(distances))

        # prints
        print(plane_equation)

        return warping_value
    
    def compute_warping2(self) -> float:
        """
        Calcula o empeno baseado nas coordenadas da nuvem de pontos.

        Esta função realiza as seguintes operações:
        1. Extrai os pontos da nuvem de pontos.
        2. Calcula o valor médio de Y para os pontos onde Z é o menor.
        3. Calcula o valor médio de Y para os pontos onde Z é o maior.
        4. Calcula a altura de referência como a média dos valores médios de Y calculados nos passos 2 e 3.
        5. Calcula o valor médio de Y para todos os pontos.
        6. Calcula o empeno como a diferença entre o valor médio de Y de todos os pontos e a altura de referência.
        7. Imprime e retorna o valor do empeno.

        Retorno:
            float: O valor do empeno em métros.

        Exemplo de uso:
            warping = self.compute_warping2()

        """
        # Extrair os pontos da nuvem de pontos
        points = np.asarray(self.point_cloud.points)
        
        # Operação para encontrar o valor médio de Y para os pontos onde Z é o menor
        mean_y_for_min_z = np.mean(points[points[:, 2] == np.min(points[:, 2]), 1])

        # Operação para encontrar o valor médio de Y para os pontos onde Z é o maior
        mean_y_for_max_z = np.mean(points[points[:, 2] == np.max(points[:, 2]), 1])

        # altura de ref
        h = (mean_y_for_min_z + mean_y_for_max_z)/2

        # Operação para encontrar o valor médio de Y entre todos os pontos
        mean_y = np.mean(points[:, 1])

        # empeno
        warping = np.abs(h - mean_y)

        return warping

    def visualize(self, visualize_plane: bool, warping_list: list):
        """
        Visualizes the point cloud.
        
        Parameters:
        visualize_plane (bool): If the plot must show the plane fitted to the point cloud.
        """
        if not visualize_plane:
            self.point_cloud.paint_uniform_color([0, 0.5, 1]) # blue
            o3d.visualization.draw_geometries([self.point_cloud])
        else:
            # vetor de tuplas [x, y, z]
            point_cloud = np.asarray(self.point_cloud.points)

            # [a, b, c, d] os coeficientes da equação do plano
            a, b, c, d = self.plane_model

            # Calculando os limites da nuvem de pontos
            x_min, x_max = np.min(point_cloud[:, 0]), np.max(point_cloud[:, 0])
            y_min, y_max = np.min(point_cloud[:, 1]), np.max(point_cloud[:, 1])
            z_min, z_max = np.min(point_cloud[:, 2]), np.max(point_cloud[:, 2])

            # Definindo a grade para o plano com base nos limites da nuvem de pontos
            x = np.linspace(x_min, x_max, 10)
            y = np.linspace(y_min, y_max, 10)
            x, y = np.meshgrid(x, y)
            z = (-a * x - b * y - d) / c

            # Limitando os valores de z para estarem dentro do intervalo [z_min, z_max]
            z = np.clip(z, z_min, z_max)

            # Criando uma nuvem de pontos no PyVista
            point_cloud_pv = pv.PolyData(point_cloud)

            # Criando a malha do plano
            plane = pv.StructuredGrid(x, y, z)

            # Criando a plotagem
            plotter = pv.Plotter()  # Assegure-se de criar um novo plotter
            plotter.add_mesh(point_cloud_pv, color='blue', point_size=5, render_points_as_spheres=True)
            plotter.add_mesh(plane, color='yellow', opacity=0.5)

            # adding a text with the measurement results
            text = ""
            for i, warping in enumerate(warping_list):
                text += f"Measured Warping by Method {i+1}: {(warping*100):.2f} cm\n"
            plotter.add_text(text, position='upper_left', font_size=12, color='red')

            plotter.show()

        print("Point cloud visualized.")
