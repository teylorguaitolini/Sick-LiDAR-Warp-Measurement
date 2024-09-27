from utils.config import Config
from utils.lms4000 import LMS4000
from utils.logger_config import logger
from utils.PointCloudManager import PointCloudManager

class Measurement:
    def __init__(self, conf: Config) -> None:
        # --- Config data --- #
        self._conf = conf
        # --- --- #

        # --- PointCloudManager object --- #
        self._pcm = PointCloudManager()
        # --- --- #

        # --- LiDAR sensor object --- #
        self._lidar = LMS4000(
            self._conf.LMS4000_ip, 
            self._conf.LMS4000_port, 
            self._conf.start_angle, 
            self._conf.stop_angle,
            self._conf.response_time,
            self._conf.reverse_direction
        )
        # --- --- #

    @property
    def warping(self):
        return self._pcm.vt_warping
    
    @property
    def warping_image(self):
        return self._pcm.vt_warping_image
    
    @property
    def lenght(self):
        return self._pcm.vt_lenght
    
    @property
    def hight(self):
        return self._pcm.vt_hight
    
    @property
    def distance(self):
        return self._pcm.vt_distance
    
    def measurement_routine(self):
        try:
            logger.info("Starting measurement.")
            
            # Perform data acquisition routine
            self._lidar.data_acquisition_routine()

            # Load point cloud into pcm
            self._pcm.load_from_list(self._lidar.pcd)

            # values must be read from the config file
            self._pcm.encoder_to_real_Z_distance(
                self._conf.pulses_per_rev, 
                self._conf.mm_per_rev
            )

            # data adequacy to the point cloud
            self._pcm.data_adequacy(mirror=True)
            
            # Apply filters to the point cloud
            self._pcm.filter_pcd(
                distance=self._conf.distance
            )

            self._pcm.data_adequacy()

            # compute warping and get the warping image
            self._pcm.virtualTwine()

            # Saving the Point Cloud as a CSV file
            self._pcm.pcd2csv(self._conf.save_point_cloud)
        
        except Exception as e:
            logger.error(f"Error in measurement routine: {e}")
            raise Exception(f"Error in measurement routine: {e}")
        