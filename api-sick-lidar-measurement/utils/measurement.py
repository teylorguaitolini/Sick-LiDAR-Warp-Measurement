import requests
from os import getcwd, makedirs
from os.path import join, exists
from datetime import datetime
from utils.config import Config
from utils.lms4000 import LMS4000
from utils.logger_config import logger
from utils.PointCloudManager import PointCloudManager

class Measurement:
    def __init__(self, conf: Config) -> None:
        self._conf = conf
        self._warping = 0.0
        self._warping_image = None

    @property
    def warping(self):
        return self._warping
    
    @property
    def warping_image(self):
        return self._warping_image
    
    def measurement_routine(self):
        try:
            logger.info("Starting measurement.")
            
            # --- LiDAR sensor object --- #
            lidar = LMS4000(self._conf.LMS4000_lidar_ip, self._conf.LMS4000_lidar_port, self._conf.LMS4000_start_angle, self._conf.LMS4000_stop_angle)

            # Start the motor
            logger.info("Starting the motor.")
            url = f"http://{self._conf._API_MOTOR_ip}:{self._conf._API_MOTOR_port}/start"
            response = requests.post(url)
            if response.status_code == 200:
                response_data = response.json()
                message = response_data.get("message")
            else:
                raise Exception(f"Error in requisition: {response.status_code}")
            
            # Check if the motor is running
            if not (message == "running"):
                raise Exception(f"Error starting the motor: {message}")
            
            logger.info("Motor started successfully.")

            # Perform data acquisition routine
            lidar.data_acquisition_routine()
            
            # --- PointCloudManager object --- #
            pcm = PointCloudManager()

            # Load point cloud into pcm
            pcm.load_from_list(lidar.pcd)
            
            # Apply filters to the point cloud
            pcm.filter_by_distance(self._conf.distance)

            # compute warping
            self._warping, self._warping_image = pcm.WMUSS()
            # pcm.WMLSS()

            # Saving the Point Cloud
            DIR = join(getcwd(), "PCDs")
            if not exists(DIR):
                makedirs(DIR)
            pcm.save_to_file(
                filename=join(DIR, str(datetime.now().strftime('%Y%m%d_%H%M%S'))), 
                format='pcd'
            )
        
        except Exception as e:
            logger.error(f"Error in measurement routine: {e}")
            raise Exception(f"Error in measurement routine: {e}")
        