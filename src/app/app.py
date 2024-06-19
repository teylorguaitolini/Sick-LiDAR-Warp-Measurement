import keyboard
from time import sleep
from datetime import datetime
from os.path import join, exists
from os import getcwd, makedirs
from tkinter import Tk, filedialog, messagebox
from config import Config
from sick.LMS4000 import LMS4000
#from sick.LMS5xx import LMS5xx
from app import PointCloudManager

class App:
    def __init__(self, conf:Config):
        # --- Dados do Arquivo de configuração --- #
        self._conf = conf
        # --- Objeto que abstrai o sensor LiDAR X --- #
        if self._conf.scan:
            #self._lidar = LMS5xx(self._conf.LMS5xx_lidar_ip, self._conf.LMS5xx_lidar_port, self._conf.LMS5xx_start_angle, self._conf.LMS5xx_stop_angle)
            self._lidar = LMS4000(self._conf.LMS4000_lidar_ip, self._conf.LMS4000_lidar_port, self._conf.LMS4000_start_angle, self._conf.LMS4000_stop_angle)
        # --- Objeto PointCloudManager --- #
        self._pcm = PointCloudManager()
    
    def flag(self):
        """
        Método para capturar o sinal de início da medição
        """
        if not self._conf.scan:
            return True
        print("Aguardando sinal para iniciar a rotina...")
        if keyboard.is_pressed('1'):
            print("Iniciando aquisição de dados...")
            return True
        else:
            return False
    
    def measurement_rotine(self):
        """
        Método principal da rotina de medição
        """
        self._lidar.data_acquisition_routine()
        # if self._conf.scan:
        #     # Realiza a rotina de aquisição dos dados de scan
        #     pcd = self._lidar.data_acquisition_routine()
        #     # carrega a nuvem no pcm
        #     self._pcm.load_from_list(pcd)

        #     # caso seja para salvar, cria o diretorio se não existir
        #     if self._conf.save:
        #         file_dir = join(getcwd(), "Measurements", str(datetime.now().strftime('%Y%m%d_%H%M%S')))
        #         if not exists(file_dir):
        #             makedirs(file_dir)

        #         # caso seja para salvar, salva a nuvem inicial
        #         self._pcm.save_to_file(
        #             filename=join(file_dir, "initial"),
        #             format="pcd"
        #             )
            
        #     # Aplica filtros na nuvem
        #     self._pcm.filter_by_distance(self._conf.distance)
        #     self._pcm.filter_statistical_outliers()

        #     # computa empenamento
        #     warping_list = []
        #     # warping_list.append(self._pcm.compute_warping())
        #     # warping_list.append(self._pcm.compute_warping2())
        #     warping_list.append(self._pcm.compute_warping3())

        #     # caso seja para salvar, salva a nuvem final e escreve resultado da mediçao
        #     if self._conf.save:
        #         self._pcm.save_to_file(
        #             filename=join(file_dir, "final"),
        #             format="pcd"
        #             )
        #         self.write_measurement_result(join(file_dir, "Measurement.txt"), warping_list)
        # else:
        #     # solicita a abertura de um arquivo pcd e já carrega no pcm
        #     self.load_file()
        #     # computa empenamento
        #     # self._pcm.compute_warping()
        #     # self._pcm.compute_warping2()
        #     self._pcm.compute_warping3()
            
        # # Abre visualização da nuvem final
        # self._pcm.visualize(visualize_plane=False)
    
    def write_measurement_result(self, filename:str, warping_list:list[float]):
        try:
            with open(filename, 'a') as file:
                file.write("# --- MEASUREMENT RESULT --- #\n")
                for i, warping in enumerate(warping_list):
                    file.write(f"Measured Warping by Method {i+1}: {(warping*100):.2f} cm\n")
                file.write("# ---")
                print(f"Mensagem gravada com sucesso em {filename}")
        except Exception as e:
            print(f"Ocorreu um erro em write_measurement_result(): {e}")
    
    def load_file(self):
        root = Tk()
        root.withdraw()

        file_path = filedialog.askopenfilename(filetypes=[("Point Cloud Data", "*.pcd *.ply")])
        if file_path:
            try:
                self._pcm.load_from_file(file_path)
                messagebox.showinfo("Sucesso", f"Arquivo carregado: {file_path}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar o arquivo: {e}")

    def end(self):
        """
        Rotina a ser executada sempre que o programa for encerrado
        """
        print("Encerrando programa...")
        if self._conf.scan:
            self._lidar.finish()

    def start(self):
        while True:
            if self.flag():
                self.measurement_rotine()
            sleep(1)
