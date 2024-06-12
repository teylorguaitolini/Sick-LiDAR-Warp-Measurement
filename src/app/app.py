import keyboard
from time import sleep
from datetime import datetime
from os.path import join, exists
from os import getcwd, makedirs
from tkinter import Tk, filedialog, messagebox
from config import Config
from sick.LMS4000 import LMS4000
from app import PointCloudManager

class App:
    def __init__(self, conf:Config):
        # --- Dados do Arquivo de configuração --- #
        self._conf = conf
        # --- Objeto que abstrai o sensor LiDAR X --- #
        if self._conf.scan:
            self._lidar = LMS4000(self._conf.lidar_ip, self._conf.lidar_port, self._conf.start_angle, self._conf.stop_angle)
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
        if self._conf.scan:
            # Realiza a rotina de aquisição dos dados de scan
            pcd = self._lidar.data_acquisition_routine()
            # carrega a nuvem no pcm
            self._pcm.load_from_list(pcd)

            # caso seja para salvar, cria o diretorio se não existir
            if self._conf.save:
                file_dir = join(getcwd(), "Measurements", str(datetime.now().strftime('%Y%m%d_%H%M%S')))
                if not exists(file_dir):
                    makedirs(file_dir)

                # caso seja para salvar, salva a nuvem inicial
                self._pcm.save_to_file(
                    filename=join(file_dir, "initial"),
                    format="pcd"
                    )
            
            # Aplica filtros na nuvem e computa empenamento
            self._pcm.filter_by_distance(self._conf.distance)
            self._pcm.filter_statistical_outliers()
            warping, plane_equation = self._pcm.compute_warping()

            # caso seja para salvar, salva a nuvem final e escreve resultado da mediçao
            if self._conf.save:
                self._pcm.save_to_file(
                    filename=join(file_dir, "final"),
                    format="pcd"
                    )
                self.write_measurement_result(join(file_dir, "Measurement.txt"), str(warping), plane_equation)
        else:
            # solicita a abertura de um arquivo pcd e já carrega no pcm
            self.load_file()
            # computa empenamento
            warping, plane_equation = self._pcm.compute_warping()
            
        # Abre visualização da nuvem final
        self._pcm.visualize()
    
    def write_measurement_result(self, filename:str, warping:str, plane_equation:str):
        try:
            with open(filename, 'a') as file:
                file.write("# --- MEASUREMENT RESULT --- #\n")
                file.write(f"{plane_equation}\n")
                file.write(f"Measured Warping: {warping} m\n")
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
