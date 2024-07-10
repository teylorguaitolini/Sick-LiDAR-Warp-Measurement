from time import sleep
from datetime import datetime
from sick.LMS4000.CoLaA_TCP import ColaA_TCP
from config.logger_config import logger

class LMS4000():
    """
    Class that abstracts the LMS4000 LiDAR sensor.
    """
    def __init__(self, ip:str, port:int, start_angle:int, stop_angle:int) -> None:
        # --- Dados provenientes no arquivo config.ini --- #
        self._ip = ip
        self._port = port
        self._start_angle = start_angle
        self._stop_angle = stop_angle
        # --- Objeto de Comunicação com o LiDAR (Protocolo CoLa A via TCP) --- #
        self._com = ColaA_TCP(self._ip, self._port)

        self._pcd = []
    
    @property
    def pcd(self):
        return self._pcd
    
    def data_acquisition_routine(self):
        """
        Method that creates the pcd list by capturing each scan requested to the sensor.
        """
        com_sts = self._com.connect()
        if not com_sts:
            return False

        param_sts = self._parameterize()
        if not param_sts:
            return False

        # if is connected and the parameterization is done
        try:
            old_Z_value = 0.0
            same_Z_value_counter = 0
            # --- Loop while Beg --- #
            while True:
                points = self._com.poll_one_telegram()

                current_Z_value = points[0][2]
                if (current_Z_value<old_Z_value):    # the lidar is mooving backward
                    logger.info("Data aquisition finished because the lidar was mooving backward.")
                    break
                elif (current_Z_value==old_Z_value): # the lidar is no longer mooving
                    same_Z_value_counter+=1
                    if same_Z_value_counter == 200:  # stopped for too long, 2.0 s
                        logger.info("Data aquisition finished because the lidar was not mooving.")
                        break
                else:                                # still mooving forward
                    old_Z_value = current_Z_value
                    same_Z_value_counter = 0

                self._pcd.extend(points)

                # Response time of 4.8 ms
                # from performance technical details in datasheet
                # sleep(4.8/1000)  
                # but I will use more time, 10 ms, so:
                sleep(10/1000)
            # --- Loop while End --- #
            self._com.release() # Finish the connection with the sensor after the measurement
        except Exception as e:
            logger.error(e)
            return False
        
        if len(self._pcd) == 0:
            logger.error("Despite no errors, no points were loaded.")
            return False

        logger.info("LiDAR data acquisition routine done.")
        return True
    
    def _parameterize(self):
        """
        Method that sends all messages of configuration.
        """
        try:
            self._com.login()
            # self._com.read_freq_and_angular_resol()
            self._com.config_scandata_content()
            # self._com.config_scandata_measurement_output(self._start_angle, self._stop_angle)
            # self._com.set_encoder_settings()
            self._com.reset_encoder_values()    # to ensure that the encoder will start at 0 mm
            self._com.logout()

            logger.info("LiDAR parameterization done.")
            return True
        except Exception as e:
            logger.error(e)
            return False
    