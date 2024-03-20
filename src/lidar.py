from sick_scan_tcp import SickScan

class LiDAR:
    def __init__(self, ip:str, port:int, min_angle:int, max_angle:int) -> None:
        self._ip = ip
        self._port = port
        self._min_angle = min_angle
        self._max_angle = max_angle

        self.lidar_sts = False
        self.cartesian = None
    
    def connect(self):
        try:
            self.sick_scan = SickScan(self._ip, self._port)
            self.sick_scan.set_start_stop_angle(self._min_angle, self._max_angle)
            print("LiDAR conectado")
            self.lidar_sts = True
        except Exception as e:
            print("Não foi possível conectar ao sensor LiDAR")
    
    def get_data(self):
        try:
            telegram = self.sick_scan.scan()
            angles, values = self.sick_scan.extract_telegram(telegram)
            self.cartesian = self.sick_scan.to_cartesian(values, angles)
        except:
            print("Erro ao ler do LiDAR")
