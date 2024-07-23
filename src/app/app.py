from tkinter import Tk, filedialog, messagebox
from config.config import Config
from utils.PointCloudManager import PointCloudManager
from config.logger_config import logger

class App:
    def __init__(self, conf:Config, DIR:str):
        self._DIR = DIR
        # --- Dados do Arquivo de configuração --- #
        self._conf = conf
        # --- Objeto PointCloudManager --- #
        self._pcm = PointCloudManager()
    
    def start(self):
        try:
            while True:
                # requests the opening of a .pcd file and loads it into the pcm
                root = Tk()
                root.withdraw()

                ans = messagebox.askyesno("Question", "Load a .pcd file?")
                if ans:
                    file_path = filedialog.askopenfilename(filetypes=[("Point Cloud Data", "*.pcd *.ply")])
                    if file_path:
                        self._pcm.load_from_file(file_path)
                        self._pcm.filter_by_distance(self._conf.distance)
                        # compute warping
                        self._pcm.WMUSS(self._conf.app_save, self._DIR)
                        # self._pcm.WMLSS()
                        messagebox.showinfo("Success", "Measurement done.")
                    else:
                        messagebox.showinfo("Info", "You must choose a .pcd file.")
                else:
                    break
        except KeyboardInterrupt:
            logger.info("The App was finished by a KeyboardInterrupt.")
        except Exception as e:
            messagebox.showerror("Erro", f"Error trying to load the file: {e}")
            logger.error(e)
