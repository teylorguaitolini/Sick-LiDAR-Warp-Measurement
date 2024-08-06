from utils import Config
from utils import logger
from utils import Measurement
from fastapi import FastAPI
from os import getcwd, path
import uvicorn

conf = Config()
conf.read_config_file(path.join(getcwd(), "api", "config.ini"))

api = FastAPI()

@api.get("/")
def get_measurement():
    logger.info("Measurement request received.")

    mea = Measurement(conf, getcwd())
    measurement_sts = mea.measuremt_rotine()

    if measurement_sts:
        logger.info("Warping Measurement Success")
        return {"warping result": f"{mea.warping*100}"}
    else:
        logger.error("Warping Measurement Error.")
        return {"warping result": "-1"}

if __name__ == "__main__":
    try:
        uvicorn.run(
                    api, 
                    host=conf.api_host, 
                    port=conf.api_port,
                    log_config=None,
                    log_level="info"
                )
    except KeyboardInterrupt:
        logger.info("The API was finished by a KeyboardInterrupt.")