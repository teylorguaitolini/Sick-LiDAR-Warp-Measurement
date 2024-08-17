import requests
import streamlit as st
from utils.logger_config import logger
from utils.config import Config

class APP:
    def __init__(self, conf: Config):
        self._conf = conf
        self.setup()

    def setup(self):
        st.title("Sistema de Medição de Empenamento")

        if st.button("Iniciar Medição"):
            self.measurement_start()
        
        if st.button("Visualizar Nuvem de Pontos"):
            pass
    
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
            url = f"http://localhost:{self._conf.API_LIDAR_port}/warping"
            response = requests.get(url)
            if response.status_code == 200:
                response_data = response.json()
                warping = float(response_data.get("warping"))
                st.write(f"Empenamento: {(warping*100):.3f} cm")
            else:
                raise Exception(f"Error in requisition: {response.status_code}")
            
            # Display warping image


        except Exception as e:
            raise Exception(f"Error displaying the results: {e}")
    
    def lidar_start(self):
        try:
            # Start the lidar
            logger.info("Starting the lidar.")
            url = f"http://localhost:{self._conf.API_LIDAR_port}/start"
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
            url = f"http://localhost:{self._conf.API_MOTOR_port}/start"
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
    
    def pcd_visualization(self):
        pass