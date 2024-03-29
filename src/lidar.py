from sick_scan_tcp import SickScan
from time import sleep

class LiDAR:
    def __init__(self, ip:str, port:int, min_angle:int, max_angle:int) -> None:
        self._ip = ip
        self._port = port
        self._min_angle = min_angle
        self._max_angle = max_angle

        self._cartesian = None
    
    def connect(self):
        while True:
            try:
                self.sick_scan = SickScan(self._ip, self._port)
                self.sick_scan.set_start_stop_angle(self._min_angle, self._max_angle)
                print("LiDAR conectado")
                break
            except:
                print("Não foi possível conectar ao sensor LiDAR")
                sleep(0.5)
    
    def get_data(self):
        try:
            telegram = self.sick_scan.scan()
            angles, values = self.sick_scan.extract_telegram(telegram)
            self._cartesian = self.sick_scan.to_cartesian(values, angles)
        except:
            print("Erro ao ler do LiDAR")
    
    @property
    def cartesian(self):
        return self._cartesian
    