import keyboard
from time import sleep
from sick.LMS4000.CoLaA_TCP import ColaA_TCP

class LMS4000():
    """
    Classe que abstrai o sensor LiDAR
    """
    def __init__(self, ip:str, port:int, min_angle:int, max_angle:int) -> None:
        # --- Dados provenientes no arquivo config.ini --- #
        self._ip = ip
        self._port = port
        self._min_angle = min_angle
        self._max_angle = max_angle
        # --- Objeto de Comunicação com o LiDAR (Protocolo CoLa A via TCP) --- #
        self._com = ColaA_TCP(self._ip, self._port)

        self.parameterize()
    

    def parameterize(self):
        """
        Configuração geral do LiDAR
            - Get frequency and resolution
            - Configure scandata content
            - Configure scandata output
        """
        self._com.login()
        self._com.read_freq_and_angular_resol()
        self._com.config_scandata_content(data_channel=False, further_data_channel=0, encoder=True)
        self._com.config_scandata_measurement_output(self._min_angle, self._max_angle)
        #self._com.set_encoder_settings()
        self._com.logout()
    
    def finish(self):
        self._com.release()
    
    def data_acquisition_routine(self):
        scans = []
        n = 0

        # mensagem de start captura de dados
        while not keyboard.is_pressed('0'):
            scans.extend(self._com.poll_one_telegram())
            print("adicionando leitura")
            n += 1
            sleep(1)
            break
        # mensagem de stop da captura de dados
        return scans
