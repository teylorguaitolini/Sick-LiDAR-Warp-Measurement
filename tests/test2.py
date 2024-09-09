import pandas as pd
import open3d as o3d
import numpy as np
import matplotlib.pyplot as plt

def virtualTwineAlgorithm(x: np.ndarray, y: np.ndarray):
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
    
    # Opcional: Visualize a borda superior (comente ou remova para a produção)
    plt.scatter(x, y, s=2, label="Perfil original")
    plt.autoscale(tight=True)
    n_ticks = 10
    plt.xticks(np.linspace(min(x), max(x), n_ticks))
    plt.yticks(np.linspace(min(y), max(y), n_ticks))
    plt.plot(unique_x, upper_edge_y, 'r-', label="Borda superior")
    plt.title('Warping Measurement by Virtual Twine Method')
    plt.legend()
    plt.grid(True)
    
    # Calcular o "warping" como a diferença entre o maior e o menor valor de y na borda superior
    print(f"Upper edge: {np.max(upper_edge_y)}")
    print(f"Lower edge: {np.min(upper_edge_y)}")
    warping = np.max(upper_edge_y) - np.min(upper_edge_y)
    print(f"Warping: {warping}")

    plt.show()

    return warping


pcd_path = "D:\\Sick-LiDAR-Warp-Measurement\\api-sick-lidar-measurement\\PCDs\\20240909_193359.csv"
pcd_df = pd.read_csv(pcd_path)
points = pcd_df.to_numpy()

x = points[:, 0]
z = points[:, 2]

res = virtualTwineAlgorithm(z, x)
