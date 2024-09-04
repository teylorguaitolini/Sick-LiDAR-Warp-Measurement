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

            self._conf.read_config_file()
            
            # --- LiDAR sensor object --- #
            lidar = LMS4000(self._conf.LMS4000_ip, self._conf.LMS4000_port, self._conf.start_angle, self._conf.stop_angle)
            
            logger.info("Motor started successfully.")

            # Perform data acquisition routine
            lidar.data_acquisition_routine()
            
            # --- PointCloudManager object --- #
            pcm = PointCloudManager()

            # Load point cloud into pcm
            pcm.load_from_list(lidar.pcd)

            # values must be read from the config file
            pcm.encoder_to_real_Z_distance(self._conf.pulses_per_rev, self._conf.mm_per_rev)
            
            # Apply filters to the point cloud
            pcm.filter_by_Y_distance(self._conf.distance, self._conf.filter_Y_iterations_num)
            
            # data adequacy to plot the point cloud
            pcm.data_adequacy()

            # compute warping and get the warping image
            self._warping, self._warping_image = pcm.virtualTwine()

            # Saving the Point Cloud as a CSV file
            pcm.pcd2csv(self._conf.save_point_cloud)
        
        except Exception as e:
            logger.error(f"Error in measurement routine: {e}")
            raise Exception(f"Error in measurement routine: {e}")
        