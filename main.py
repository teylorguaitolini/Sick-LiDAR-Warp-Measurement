from src.config import Config
from src.app import App

if __name__ == "__main__":
    conf = Config()
    conf.read_config_file()

    app = App(conf)
    app.start()
