import pandas as pd
import open3d as o3d



pcd_path = "D:\\Sick-LiDAR-Warp-Measurement\\api-sick-lidar-measurement\\PCDs\\20240909_181029.csv"

pcd_df = pd.read_csv(pcd_path)

points = pcd_df.to_numpy()

pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(points)
o3d.visualization.draw_geometries([pcd])
