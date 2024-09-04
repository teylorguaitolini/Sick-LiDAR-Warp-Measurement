import base64
import requests
import open3d as o3d
import numpy as np
import streamlit as st
import pyvista as pv
import pandas as pd
from stpyvista import stpyvista
from PIL import Image
from io import BytesIO
from utils.config import Config
from utils.logger_config import logger

class APP:
    def __init__(self, conf: Config):
        self._conf = conf
        self.setup()

    def setup(self):
        st.title("Sistema de Medição de Empeno")

        if st.button("Iniciar Medição"):
            self.measurement_start()
    
    def measurement_start(self):
        try:
            self.motor_start()
            self.lidar_start()
            self.display_results()
        except Exception as e:
            logger.error(f"Error in measurement rotine: {e}")
            st.error("Erro na rotina de medição.")
    
    def display_results(self):
        try:

            # Display warping value
            url = f"http://{self._conf._API_LIDAR_host}:{self._conf.API_LIDAR_port}/warping"
            response = requests.get(url)
            if response.status_code == 200:
                response_data = response.json()
                warping = float(response_data.get("warping"))
                st.write(f"Empeno: {(warping*100):.3f} cm")
            else:
                raise Exception(f"Error in requisition. Status Code: {response.status_code}")
            
            # Display warping image
            url = f"http://{self._conf._API_LIDAR_host}:{self._conf.API_LIDAR_port}/warping_image"
            response = requests.get(url)
            if response.status_code == 200:
                response_data = response.json()
                warping_image = response_data.get("warping_image")
                image_data = base64.b64decode(warping_image)
                image = Image.open(BytesIO(image_data))
                st.image(image, caption="Imagem do Empeno", use_column_width=True)
            else:
                raise Exception(f"Error in requisition. Status Code: {response.status_code}")
            
            # Display point cloud
            # url = f"http://localhost:{self._conf.API_LIDAR_port}/pcd"
            # response = requests.get(url)
            # if response.status_code == 200:
            #     response_data = response.json()
            #     json_pcd = response_data.get("pcd")
            #     df = pd.read_json(json_pcd, orient='records')
            #     points = df.to_numpy()
               
            #     pcd = o3d.geometry.PointCloud()
            #     pcd.points = o3d.utility.Vector3dVector(points)
            #     o3d.visualization.draw_geometries([pcd])
            #     # print(np.asarray(pcd.points))
            #     # # Create a plot using PyVista
            #     # cloud = pv.PolyData(pcd.points)
                
            #     # if cloud.n_points == 0:
            #     #     raise Exception("The point cloud resulted in an empty mesh.")
                
            #     # plotter = pv.Plotter()
            #     # plotter.add_mesh(cloud, color='white', point_size=2)
            #     # plotter.view_isometric()
            #     # plotter.show_bounds(grid='front', location='all', color='gray')
                
            #     # # Display the visualization in Streamlit
            #     # stpyvista(plotter, key="3d_plot")
            # else:
            #     raise Exception(f"Error in requisition. Status Code: {response.status_code}")

        except Exception as e:
            raise Exception(f"Error displaying the results: {e}")
    
    def lidar_start(self):
        try:
            # Start the lidar
            logger.info("Starting the lidar.")
            url = f"http://{self._conf._API_LIDAR_host}:{self._conf.API_LIDAR_port}/start"
            response = requests.post(url)
            if response.status_code == 200:
                response_data = response.json()
                message = response_data.get("message")
                if message == "error":
                    raise Exception("Error detected by the API.")
            else:
                raise Exception(f"Error in requisition: {response.status_code}")
        except Exception as e:
            raise Exception(f"Error starting the lidar: {e}")
    
    def motor_start(self):
        try:
            # Start the motor
            logger.info("Starting the motor.")
            url = f"http://{self._conf._API_MOTOR_host}:{self._conf.API_MOTOR_port}/start"
            response = requests.post(url)
            if response.status_code == 200:
                response_data = response.json()
                message = response_data.get("message")
                if message == "error":
                    raise Exception("Error detected by the API.")
            else:
                raise Exception(f"Error in requisition: {response.status_code}")
        except Exception as e:
            raise Exception(f"Error starting the motor: {e}")
    