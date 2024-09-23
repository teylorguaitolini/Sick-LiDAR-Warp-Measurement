import pandas as pd
import open3d as o3d
import numpy as np
import matplotlib.pyplot as plt

# Carregar o CSV contendo os pontos da nuvem
pcd_path = "D:\\Sick-LiDAR-Warp-Measurement\\api-sick-lidar-measurement\\PCDs\\20240919_162657.csv"
pcd_df = pd.read_csv(pcd_path)

# Converter para NumPy
points = pcd_df.to_numpy()

# Criar o objeto PointCloud e atribuir os pontos
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(points)

# Normalizar os valores do eixo Y para o range [0, 1]
y_values = points[:, 1]  # Eixo Y
y_min = y_values.min()
y_max = y_values.max()
normalized_y = (y_values - y_min) / (y_max - y_min)

# Gerar cores com base no valor normalizado de Y, usando um mapa de calor (por exemplo, o viridis)
colormap = plt.get_cmap("Spectral")
# colormap = plt.get_cmap("Greys")
colors = colormap(normalized_y)[:, :3]  # Obter RGB do colormap

# Atribuir as cores aos pontos da nuvem
pcd.colors = o3d.utility.Vector3dVector(colors)

# Visualizar a nuvem de pontos com cores baseadas no eixo Y
o3d.visualization.draw_geometries([pcd])

