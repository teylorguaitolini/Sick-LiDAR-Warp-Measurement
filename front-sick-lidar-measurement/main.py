from utils import APP, logger, Config

if __name__ == "__main__":
    try:
        conf = Config()
        conf.read_config_file()

        app = APP(conf)
    except Exception as e:
        logger.error(e)