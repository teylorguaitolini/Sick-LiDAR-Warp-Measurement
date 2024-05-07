from config.config import Config
from app.app import App

if __name__ == "__main__":
    conf = Config()
    conf.read_config_file()

    app = App(conf)
    app.start()
