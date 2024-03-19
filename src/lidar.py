from sick_scan_tcp import SickScan

class LiDAR:
    def __init__(self, ip:str, port:int, min_angle:int, max_angle:int) -> None:
        self.__ip = ip
        self.__port = port
        self.__min_angle = min_angle
        self.__max_angle = max_angle

        self.lidar_sts = False
        self.cartesian = None
    
    def connect(self):
        try:
            self.sick_scan = SickScan(self.__ip, self.__port)
            self.sick_scan.set_start_stop_angle(self.__min_angle, self.__max_angle)
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
