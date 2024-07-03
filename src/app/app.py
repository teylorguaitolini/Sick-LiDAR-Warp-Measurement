from datetime import datetime
from os.path import join, exists
from os import getcwd, makedirs
from tkinter import Tk, filedialog, messagebox
from config.config import Config
from utils.PointCloudManager import PointCloudManager

class App:
    def __init__(self, conf:Config):
        # --- Dados do Arquivo de configuração --- #
        self._conf = conf
        # --- Objeto PointCloudManager --- #
        self._pcm = PointCloudManager()
    
    def _write_measurement_result(self, filename:str, warping_list:list):
        try:
            with open(filename, 'a') as file:
                file.write("# --- MEASUREMENT RESULT --- #\n")
                for i, warping in enumerate(warping_list):
                    file.write(f"Measured Warping by Method {i+1}: {(warping*100):.2f} cm\n")
                file.write("# ---")
                print(f"Mensagem gravada com sucesso em {filename}")
        except Exception as e:
            print(f"Ocorreu um erro em write_measurement_result(): {e}")
    
    def _load_file(self):
        root = Tk()
        root.withdraw()

        file_path = filedialog.askopenfilename(filetypes=[("Point Cloud Data", "*.pcd *.ply")])
        if file_path:
            try:
                self._pcm.load_from_file(file_path)
                messagebox.showinfo("Sucesso", f"Arquivo carregado: {file_path}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar o arquivo: {e}")

    def _end(self):
        """
        Rotina a ser executada sempre que o programa for encerrado
        """
        print("Encerrando programa...")

    def start(self):
        try:
            while True:
                # requests the opening of a .pcd file and loads it into the pcm
                self._load_file()

                # compute warping
                warping_list = []
                warping_list.append(self._pcm.compute_warping())
                warping_list.append(self._pcm.compute_warping2())
                warping_list.append((warping_list[0] + warping_list[1])/2)
                
                if self._conf.app_save:
                    # create the directory to save the measurement
                    file_dir = join(getcwd(), "Measurements", str(datetime.now().strftime('%Y%m%d_%H%M%S')))
                    if not exists(file_dir):
                        makedirs(file_dir)

                    # whrite the measurement results into a .txt file
                    self._write_measurement_result(join(file_dir, "Measurement.txt"), warping_list)

                # Open the visualization of the pcd
                self._pcm.visualize(visualize_plane=True, warping_list=warping_list)
        except KeyboardInterrupt:
            print("Programa interrompido pelo usuário.")
        finally:
            self._end()
