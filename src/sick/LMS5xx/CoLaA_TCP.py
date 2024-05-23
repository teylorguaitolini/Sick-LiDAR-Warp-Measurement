import socket
import math
import struct
import time

class ColaA_TCP():
    """
    Classe que implementa a comunicação protocolo CoLa A da Sick via TCP com o sensor x
    """
    def __init__(self, ip:str, port:int) -> None:
        # --- Dados do arquivo de configuração --- #
        self._ip = ip
        self._port = port
        # --- Objeto comunicação Socket --- #
        self.socket_sick = None
    
    def connect(self) -> None:
        """
        Cria a conexão Socket com o LiDAR
        """
        try:
            self.socket_sick = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_sick.connect((self._ip, self._port))
            print("Conexão socket criada")
        except Exception as e:
            print(f"Erro ao tentar criar a conexão socket: {e}")

    
    def release(self) -> None:
        """
        Termina a Conexão Socket com o LiDAR
        """
        self.socket_sick.close()
        print("Conexão socket encerrada")
    
    @staticmethod
    def int_2hex(decimal_number, factor) -> str:
        return hex(int(decimal_number * factor))[2:].upper()
    
    @staticmethod
    def int_2hexstring(decimal_number) -> str:
        return hex(decimal_number)[2:].upper()
    
    @staticmethod
    def hex_to_meters(i) -> list[float]:
        i = [int(x,16)/1000 for x in i ]
        return i
    
    @staticmethod
    def uint32(i):
        i = struct.unpack('>i', bytes.fromhex(i))[0]
        return i

    @staticmethod
    def remove_outprov(data: str) -> str:
        data = data.replace('\x02','')
        data = data.replace('\x03','')
        return data
    
    @staticmethod
    def to_cartesian(
            distances: list[float], 
            angles: list[float]
        ) -> tuple[list[float], list[float]]:
        x = list(map(lambda r, t: r * math.cos(math.radians(t)), distances, angles))
        y = list(map(lambda r, t: r * math.sin(math.radians(t)), distances, angles))
        return x, y
    
    def send_socket(
            self,
            message : str,
            buffer : int
        ) -> str:
        print("sending message: "+ message)
        try:
            message = f'\x02{message}\x03'.encode()
            self.socket_sick.send(message)
        except ConnectionAbortedError:
            self.connect()
            time.sleep(0.1)
        finally:
            message = f'\x02{message}\x03'.encode()
            self.socket_sick.send(message)

        data = self.socket_sick.recv(buffer)
        data = data.decode()
        data = self.remove_outprov(data=data)
        print("received message: "+ data)
        return data
    
    """
    # --- Implementação das mensagens --- #
    """

    def login(self):
        """
        Envia a mensagem para logar como Authorized Client
        """
        try:
            data = self.send_socket(
                message = "sMN SetAccessMode 03 F4724744",
                buffer = 128
            )
            telegram = data.split()
            if telegram[2] == "1":
                print("logado")
                return True
            else:
                return False
        except Exception as e:
            print(f"Erro ao realizar o login {e}")
            return False
    
    def logout(self):
        """
        Encerra o login de Authorized Client
        """
        data = self.send_socket(
            message = "sMN Run",
            buffer = 128
        )
        telegram = data.split()
        if telegram[2] == "1":
            print("deslogado")
            return True
        else:
            return False
    
    def set_scan_config(self, scan_freq:int, angular_resol:int):
        """
        Configura a Frequência de scan e a Resolução angular
        \nscan_freq = 25, 35, 50, 75 e 100 Hz
        \nangular_resol = 0.1667°, 0.25°, 0.333°, 0.5°, 0.667° e 1°
        """
        msg = f"sMN mLMPsetscancfg {self.int_2hex(scan_freq, 100)} 1 {self.int_2hex(angular_resol, 10000)} FFFF3CB0 1C3A90"
        data = self.send_socket(
            message = msg,
            buffer = 128
        )
        print(data)
        telegram = data.split()
        if telegram[2] == "0":
            print("sucesso")
            scan_freq = int(telegram[3], 16)/100                # Hz
            num_of_sectors = int(telegram[4])                   # 1 sempre
            angular_resolution = int(telegram[5], 16)/10000     # graus
            start_angle = self.uint32(telegram[6])/10000        # sempre -5°
            stop_angle = int(telegram[7], 16)/10000             # sempre 185°
            print(scan_freq)
            print(num_of_sectors)
            print(angular_resolution)
            print(start_angle)
            print(stop_angle)
            return True
        else:
            if telegram[2] == "1":
                print("Frequency error")
            elif telegram[2] == "2":
                print("Resolution error")
            elif telegram[2] == "3":
                print("Resolution and scanarea error")
            elif telegram[2] == "4":
                print("Scanarea error")
            else:
                print("Other errors")
            return False

    def get_scan_config(self):
        data = self.send_socket(
            message = "sRN LMPscancfg",
            buffer = 128
        )
        telegram = data.split()
        scan_freq = int(telegram[2], 16)/100                # Hz
        num_of_sectors = int(telegram[3])                   # 1 sempre
        angular_resolution = int(telegram[4], 16)/10000     # graus
        start_angle = self.uint32(telegram[5])/10000        # sempre -5°
        stop_angle = int(telegram[6], 16)/10000             # sempre 185°
        print(scan_freq)
        print(num_of_sectors)
        print(angular_resolution)
        print(start_angle)
        print(stop_angle)
