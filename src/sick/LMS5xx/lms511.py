from sick.LMS4000.CoLaA_TCP import ColaA_TCP

class LMS511():
    """
    Classe que abstrai o sensor LiDAR
    """
    def __init__(self, ip:str, port:int, start_angle:int, stop_angle:int) -> None:
        # --- Dados provenientes no arquivo config.ini --- #
        self._ip = ip
        self._port = port
        self._start_angle = start_angle
        self._stop_angle = stop_angle
        # --- Objeto de Comunicação com o LiDAR (Protocolo CoLa A via TCP) --- #
        self._com = ColaA_TCP(self._ip, self._port)

        self.parameterize(10000, 10000, self._start_angle, self._stop_angle)
    

    def parameterize(self, scan_freq:int, angular_resol:int, start_angle:int, stop_angle:int):
        """
        Configuração geral do LiDAR
        \nSet frequency and resolution
        \nConfigure scandata content
        \nConfigure scandata output
        """
        if self._com.connect():
            self._com.login()

            self._com.set_scan_config(scan_freq, angular_resol)

            self._com.logout()
            self._com.release()

        