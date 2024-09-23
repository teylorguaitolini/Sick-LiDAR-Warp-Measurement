from time import sleep
from datetime import datetime
from utils.CoLaA_TCP import CoLaA_TCP
from utils.logger_config import logger

class LMS4000():
    """
    Class that abstracts the LMS4000 LiDAR sensor.
    """
    def __init__(
        self, 
        ip:                str, 
        port:              int, 
        start_angle:       int, 
        stop_angle:        int,
        response_time:     float,
        reverse_direction: bool
    ):
        # --- Objeto de Comunicação com o LiDAR (Protocolo CoLa A via TCP) --- #
        self._cola = CoLaA_TCP(ip, port)
        # ---  --- #

        # --- Dados provenientes no arquivo config.ini --- #
        self._start_angle = start_angle
        self._stop_angle = stop_angle
        self._response_time = response_time
        self._reverse_direction = reverse_direction
        # ---  --- #

        # --- Dados Processados --- #
        self._pcd = []
        self._encoder_value_current = 0.0
        self._encoder_value_previous = 0.0
        self._start_time = None
        self._direction = ""
        self._previous_direction = ""
        # ---  --- #
    
    @property
    def pcd(self):
        return self._pcd
    
    def data_acquisition_routine(self):
        """
        Method that creates the pcd list by capturing each scan requested to the sensor.
        """
        try:            
            self._cola.connect()

            self._parameterize()

            # if it is connected and the parameterization is done, start the data acquisition

            # --- Resetting the variables --- #
            self._pcd = []
            self._direction = "S"
            self._previous_direction = "S"
            self._encoder_value_previous = 0.0
            self._encoder_value_current = 0.0
            self._start_time = datetime.now()
            # ---  --- #

            self._cola.poll_one_telegram() # to clear the buffer
            print(self._reverse_direction)
            # --- Loop while Beg --- #
            while True:
                # Receiving the scan data
                points = self._cola.poll_one_telegram()
                
                # --- Logic to stop the data acquisition --- #
                self._update_direction(points)
                print(self._direction)
                if self._stop_acquisition_conditions(reversible=self._reverse_direction):
                    break
                # ---  --- #

                # Appending the points to the pcd list
                self._pcd.extend(points)

                # wainting the sensor response time
                sleep(self._response_time / 1000)
            # --- Loop while End --- #

            self._cola.release() # Finish the connection with the sensor after the measurement
        
            if len(self._pcd) == 0:
                logger.error("Despite no errors, no points were loaded.")
                raise Exception("No points were loaded.")

            logger.info("LiDAR data acquisition routine done.")

        except Exception as e:
            logger.error(f"Error in data acquisition routine: {e}")
            raise Exception(f"Error in data acquisition routine: {e}")
    
    def _update_direction(self, points: list[tuple[float, float, int]]):
        self._encoder_value_previous = self._encoder_value_current
        self._encoder_value_current = points[0][2]

        self._previous_direction = self._direction

        if self._encoder_value_current > self._encoder_value_previous:
            # the lidar is mooving to the left now
            self._direction = "L"
        elif self._encoder_value_current < self._encoder_value_previous:
            # the lidar is mooving to the right now
            self._direction = "R"
        else:
            # the lidar is in the same position
            self._direction = "S"
    
    def _check_encoder_overflow(self):
        MAX_ENCODER_VALUE = 0xFFFFFFFF

        if self._encoder_value_current < self._encoder_value_previous:
            # Verifica overflow crescente (FFFFFFFFh -> 0h)
            if self._encoder_value_previous - self._encoder_value_current > (MAX_ENCODER_VALUE / 2):
                return True

        elif self._encoder_value_current > self._encoder_value_previous:
            # Verifica overflow decrescente (0h -> FFFFFFFFh)
            if self._encoder_value_current - self._encoder_value_previous > (MAX_ENCODER_VALUE / 2):
                return True

        return False    # the data acquisition must continue

    def _stop_acquisition_conditions(self, reversible: bool):
        if self._check_encoder_overflow():
            logger.info("Data aquisition finished because the encoder overflowed.")
            return True

        if self._direction == "S":
            if (datetime.now()-self._start_time).seconds >= 2:  # stopped for too long, 2.0 s
                logger.info("Data aquisition finished because the lidar was not mooving.")
                return True
            
            if (not reversible) and (self._previous_direction != "S"):
                logger.info("Data aquisition finished because the lidar changed the direction.")
                return True
        else:
            self._start_time = datetime.now()

            if (not reversible) and (self._previous_direction != "S") and (self._direction != self._previous_direction):
                logger.info("Data aquisition finished because the lidar changed the direction.")
                return True
            
        return False    # the data acquisition must continue

    def _parameterize(self):
        """
        Method that sends all messages of configuration.
        """
        try:
            self._cola.login()
            # self._cola.read_freq_and_angular_resol()
            self._cola.config_scandata_content()
            self._cola.config_scandata_measurement_output(self._start_angle, self._stop_angle)
            self._cola.set_encoder_settings()
            self._cola.reset_encoder_values()    # to ensure that the encoder will start at 0 mm
            self._cola.logout()

            logger.info("LiDAR parameterization done.")
        except Exception as e:
            logger.error(f"Error in parameterization: {e}")
            raise Exception(f"Error in parameterization: {e}")
    