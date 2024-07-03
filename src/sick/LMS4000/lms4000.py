from time import sleep
from datetime import datetime
from sick.LMS4000.CoLaA_TCP import ColaA_TCP

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

        self._parameterize()

    def _parameterize(self):
        """
        Configuração geral do LiDAR
            - Get frequency and resolution
            - Configure scandata content
            - Configure scandata output
        """
        self._com.login()
        self._com.read_freq_and_angular_resol()
        self._com.config_scandata_content()
        #self._com.config_scandata_measurement_output(self._start_angle, self._stop_angle)
        #self._com.set_encoder_settings()
        # to ensure that the encoder will start at 0 mm
        self._com.reset_encoder_values()
        self._com.logout()
    
    def finish(self):
        self._com.release()
    
    def data_acquisition_routine(self):
        """
        Method that creates the pcd list by capturing each scan requested to the sensor.
        """
        pcd = []
        start_time = datetime.now()
        while (datetime.now() - start_time).seconds <= 10:
            points = self._com.poll_one_telegram()
            pcd.extend(points)
            print(points[0][2]) # printing the z axis to debug
            sleep(0.25)
        return pcd