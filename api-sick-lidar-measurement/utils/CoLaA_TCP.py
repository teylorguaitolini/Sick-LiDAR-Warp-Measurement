import socket
import math
import struct
import time
from datetime import datetime
from utils.logger_config import logger

class ColaA_TCP():
    """
    Class that implements the comunication by Sick CoLa A protocol via TCP with the LMS4000 sensor.
    """
    def __init__(self, ip:str, port:int) -> None:
        # --- Dados do arquivo de configuração --- #
        self._ip = ip
        self._port = port
        # --- Objeto comunicação Socket --- #
        self.socket_sick = None
    
    @staticmethod
    def int_2hex(decimal_number, factor) -> str:
        return hex(int(decimal_number * factor))[2:].upper()
    
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
        #print("sending message: "+ message)
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
        #print("received message: "+ data)
        return data
    
    def extract_telegram(self, data: str):
        try:
            telegram = data.split()
            head = telegram[:18]
            encoder = telegram[18:21]
            body = telegram[21:]
            #print(len(telegram))
            #print("Head: " + str(head))
            #print("Encoder: " + str(encoder))
            #print("Body:" + str(body))

            scale_factor = 0.1 # for LMS4000: Factor x 0.1: 3DCCCCCDh (DIST1)
            try:
                start_angle = self.uint32(body[4])/10000.0
            except ValueError:
                start_angle = int(body[4], 16)/10000.0
            angle_step = int(body[5], 16) / 10000.0
            value_count = int(body[6], 16)   
            distances = list(map(lambda x: (int(x, 16) * scale_factor)/1000.0, body[7:7+value_count]))
            angles = [start_angle + angle_step * n for n in range(value_count)]

            x, y = self.to_cartesian(distances, angles)

            encoder_resolution = 0.2 # 0.2 mm per tick
            encoder_current_num_of_ticks = int(encoder[1], 16)
            current_position = (encoder_current_num_of_ticks * encoder_resolution / 1000) # in meters

            z = [current_position] * len(x)

            # transforma do formato ([x1, x2, x3, ...], [y1, y2, y3, ...], [z1, z2, z3, ...])
            # para o formato ([x1, y1, z1], [x2, y2, z2], [x3, y3, z3], ...)
            points = list(zip(*(x, y, z)))
            return points
        except Exception as e:
            raise e

    def connect(self):
        """
        Cria a conexão Socket com o LiDAR
        """
        try:
            logger.info("Trying to connect with LiDAR.")
            self.socket_sick = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_sick.connect((self._ip, self._port))
            logger.info("socket connection has been created with LiDAR.")
        except Exception as e:
            raise Exception(f"Error in connect(): {e}")
    
    def release(self) -> None:
        """
        Termina a Conexão Socket com o LiDAR
        """
        try:
            self.socket_sick.close()
            logger.info("Socket connection closed.")
        except Exception as e:
            raise e

    """
    # --- Implementação das mensagens --- #
    """

    def login(self):
        """
        Sends the message to login as Authorized Client
        """
        try:
            data = self.send_socket(
                message = "sMN SetAccessMode 03 F4724744",
                buffer = 128
            )
            telegram = data.split()
        except Exception as e:
            raise e

        if not (telegram[2] == "1"):
            raise Exception("Could not login in LiDAR.")

    def logout(self):
        """
        Logout the Authorized Client login
        """
        try:
            data = self.send_socket(
                message = "sMN Run",
                buffer = 128
            )
            # telegram = data.split()
            # if telegram[2] == "1":
            #     print("deslogado")
            #     return True
            # else:
            #     return False
        except Exception as e:
            raise e

    def read_freq_and_angular_resol(self):
        """
        Requests to the sensor sends its actual internal configurations.
        - Scan frequency        ->  Fixed in 600Hz for LMS4000
        - Number of sectors     ->  Fixed in 1 sector
        - Angular resolution    ->  Fixed in 1/12° = 0.0833...°
        - Start angle           ->  Fixed in 55°
        - Stop angle            ->  Fixed in 125°
        """
        try:
            data = self.send_socket(
                message = "sRN LMPscancfg",
                buffer = 128
            )
            telegram = data.split()
            scan_freq = int(telegram[2], 16)/100            
            num_of_sectors = int(telegram[3])                  
            angular_resolution = int(telegram[4], 16)/10000     
            start_angle = int(telegram[5], 16)/10000        
            stop_angle = int(telegram[6], 16)/10000             
            print(scan_freq)
            print(num_of_sectors)
            print(angular_resolution)
            print(start_angle)
            print(stop_angle)
            return True
        except Exception as e:
            print(f"Erro em read_freq_and_angular_resol(): {e}")
            return False
    
    def config_scandata_content(self, data_channel=True, further_data_channel=2, encoder=True):
        """
        Sessão "4.3.1 Configure the data content for the scan" do manual do Protocolo CoLa A

        Configura o conteúdo dos dados de varredura (scan) para o sensor LMS4000 utilizando o formato de telegrama CoLa A (ASCII).

        Data Channel:
        - Descrição: 
            - data_channel: Define se os valores de distância devem ser incluídos no telegrama de saída.
        - Valores:
            - `True`: "01" - Distance values (com valores de distância)
            - `False`: "00" - No distance values (sem valores de distância)
        
        Further Data Channel:
        - Descrição: 
            - further_data_channel: Configura dados adicionais transmitidos além dos valores de distância.
        - Valores:
            - `0` - No values (sem valores)
            - `1` - Remission only (apenas remissão)
            - `2` - Angle only (apenas ângulo)
            - `3` - Remission & Angle (remissão e ângulo)
            - `4` - Quality only (apenas qualidade)
            - `5` - Remission & Quality (remissão e qualidade)
            - `6` - Angle & Quality (ângulo e qualidade)
            - `7` - Remission, Angle & Quality (remissão, ângulo e qualidade)
        
        Encoder:
        - Descrição:
            - encoder: Configura se serão transmitidos dados de encoder.
        - Valores:
            - `True`: "01" - Channel 1 (com dados de encoder)
            - `False`: "00" - No encoder (sem dados de encoder)
        
        Exemplos:
            - Chamada: config_scandata_content(data_channel=False, further_data_channel=0, encoder=False)
                - Mensagem: "sWN LMDscandatacfg 00 00 0 1 0 00 00 0 0 0 0 +1"
            - Chamada: config_scandata_content(data_channel=False, further_data_channel=0, encoder=True)
                - Mensagem: "sWN LMDscandatacfg 00 00 0 1 0 01 00 0 0 0 0 +1"
            - Chamada: config_scandata_content()
                - Mensagem: "sWN LMDscandatacfg 01 00 2 1 0 01 00 0 0 0 0 +1"
        """
        try:
            p_data_channel = "01" if data_channel else "00"
            p_further_data_channel = str(further_data_channel)
            p_encoder = "01" if encoder else "00"
            data = self.send_socket(
                message = f"sWN LMDscandatacfg {p_data_channel} 00 {p_further_data_channel} 1 0 {p_encoder} 00 0 0 0 0 +1",
                buffer = 128
            )
            telegram = data.split()
        except Exception as e:
            raise e
        
        if not (telegram[1] == "LMDscandatacfg"):
            raise Exception("Error trying to configure scan data.")
    
    def config_scandata_measurement_output(self, start_angle:int, stop_angle:int):
        """
        Sessão "4.3.2 Configure measurement angle of the scandata for output" do manual do Protocolo CoLa A
            - Configura a saída da medição do sensor.
            - Obs: essa não é uma alteração nas configurações intrínsecas de scan do sensor, é apenas na disponibilização da saída. 
        """
        try:
            hex_start_angle = self.int_2hex(start_angle, 10000)
            hex_stop_angle = self.int_2hex(stop_angle, 10000)
            data = self.send_socket(
                message = f"sWN LMPoutputRange 1 341 {hex_start_angle} {hex_stop_angle}",
                buffer = 128
            )
            telegram = data.split()
        except Exception as e:
            raise e
        
        if not (telegram[1] == "LMPoutputRange"):
            raise Exception("Error trying to configure angular range in the scan data output.")

    def set_encoder_settings(self):
        """
        Sessão "4.6.2 Set encoder settings" do manual do Protocolo CoLa A
        """
        pass

    def reset_encoder_values(self):
        """
        Section "4.6.7 Reset encoder values" from the Sick Telegram Listing
        """
        try:
            data = self.send_socket(
                message = "sMN LIDrstencoderinc",
                buffer = 128
            )
            if (data[2] == "0"):
                raise Exception("Error trying to reset encoder values.")
        except Exception as e:
            raise e
        
    
    def poll_one_telegram(self):
        try:
            data = self.send_socket(
                message = 'sRN LMDscandata',
                buffer = 10240
            )
            points = self.extract_telegram(data)
            return points
        except Exception as e:
            raise e
