import base64
import requests
import open3d as o3d
import numpy as np
import streamlit as st
import pyvista as pv
import pandas as pd
import threading
from stpyvista import stpyvista
from PIL import Image
from io import BytesIO
from utils.config import Config
from utils.logger_config import logger
from time import sleep

class APP:
    def __init__(self, conf: Config):
        self._conf = conf

        self._measurement_data = None
        self._lidar_thread = None
        self._motor_thread = None

        self._setup()

    def _setup(self):
        st.title("Sistema de Medição de Empeno")

        if st.button("Iniciar Medição"):
            try:
                self._start_lidar_async()
                self._start_motor_async()
                
                while self._lidar_thread.is_alive():
                    sleep(1)
                
                self._display_results()
            except Exception as e:
                logger.error(f"Error in the measurement: {e}")
                st.error("Erro na medição. Verifique o log para mais informações.")
        
    def _display_results(self):
        try:

            url = f"http://{self._conf._API_LIDAR_host}:{self._conf.API_LIDAR_port}/results"
            response = requests.get(url)
            if response.status_code == 200:
                response_data = response.json()
                st.write(f"Empeno: {(response_data.get('warping') * 100):.3f} cm")
                st.write(f"Comprimento: {response_data.get('length'):.3f} m")
                st.write(f"Altura: {response_data.get('height'):.3f} m")
                st.write(f"Distância até o LiDAR: {response_data.get('distance'):.3f} m")

                image_data = base64.b64decode(response_data.get('warping_image'))
                image = Image.open(BytesIO(image_data))
                st.image(image, caption="Imagem do Empeno", width=800)

                #     # plotter = pv.Plotter()
                #     # plotter.add_mesh(cloud, color='white', point_size=2)
                #     # plotter.view_isometric()
                #     # plotter.show_bounds(grid='front', location='all', color='gray')
                    
                #     # # Display the visualization in Streamlit
                #     # stpyvista(plotter, key="3d_plot")
            else:
                raise Exception(f"Error in requisition. Status Code: {response.status_code}")

        except Exception as e:
            raise Exception(f"Error displaying the results: {e}")
        
    def _threads_status(self):
        lidar_sts = (self._lidar_thread is None) or (not self._lidar_thread.is_alive())
        motor_sts = (self._motor_thread is None) or (not self._motor_thread.is_alive())
        return lidar_sts and motor_sts

    def _start_lidar_async(self):
        # Criar uma thread para executar o método lidar_start
        self._lidar_thread = threading.Thread(target=self._lidar_start)
        self._lidar_thread.start()  # Iniciar a thread

    def _start_motor_async(self):
        # Criar uma thread para executar o método motor_start
        self._motor_thread = threading.Thread(target=self._motor_start)
        self._motor_thread.start()
    
    def _lidar_start(self):
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
            logger.error(f"Error starting the lidar: {e}")
    
    def _motor_start(self):
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
            logger.error(f"Error starting the motor: {e}")
    