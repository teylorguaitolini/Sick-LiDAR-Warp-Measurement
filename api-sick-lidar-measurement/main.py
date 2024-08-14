from utils import API, Config, logger

if __name__ == "__main__":
    try:
        conf = Config()
        conf.read_config_file()
        logger.info("Configuration file was read.")

        api = API(conf)
        api.start()
    except Exception as e:
        logger.error(e)
        