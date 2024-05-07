from sick_scan_tcp import SickScan
from time import sleep

class LiDAR:
    """
    Objeto que abstrai o sensor LiDAR
    """
    def __init__(self, ip:str, port:int, min_angle:int, max_angle:int) -> None:
        # --- Dados provenientes no arquivo config.ini --- #
        self._ip = ip
        self._port = port
        self._min_angle = min_angle
        self._max_angle = max_angle
        # --- Objeto de Comunicação com o LiDAR (Protocolo CoLa A via TCP) --- #
        self._sick_scan = None

        self._connect()

    def _connect(self):
        while True:
            try:
                self._sick_scan = SickScan(self._ip, self._port)
                self._sick_scan.set_start_stop_angle(self._min_angle, self._max_angle)
                print("LiDAR conectado")
                break
            except:
                print("Não foi possível conectar ao sensor LiDAR")
                sleep(0.5)
    
    def get_polar_data(self):
        try:
            telegram = self._sick_scan.scan()
            return self._sick_scan.extract_telegram(telegram)
        except:
            print("Erro ao ler do LiDAR: get_polar_data()")
    
    def get_cartesian_data(self):
        try:
            angles, values = self.get_polar_data()
            return self._sick_scan.to_cartesian(values, angles)
        except:
            print("Erro ao ler do LiDAR: get_cartesian_data()")
    