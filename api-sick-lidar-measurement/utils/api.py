import uvicorn
from fastapi import FastAPI
from utils import logger, Config, Measurement

class API:
    def __init__(self, conf: Config):
        self.conf = conf

        self.measure = Measurement(conf)

        self.app = FastAPI()

        @self.app.post("/start")
        def start_measurement():
            try:
                logger.info("Measurement start request received.")

                self.measure.measurement_routine()

                logger.info("Warping Measurement Success")

                return {"message": "success"}    
            except:
                logger.error("Warping Measurement Error.")
                return {"message": "error"}
        
        @self.app.get("/warping")
        def get_warping():
            logger.info("Warping result request received.")
            return {"warping": f"{self.measure.warping}"}
        
        @self.app.get("/warping_image")
        def get_warping_image():
            logger.info("Warping image request received.")
            return {"warping_image": self.measure.warping_image}

    def start(self):
        try:
            uvicorn.run(
                self.app, 
                host=self.conf.API_host, 
                port=self.conf.API_port,
                log_config=None
            )
        except KeyboardInterrupt:
            logger.info("The API was finished by a KeyboardInterrupt.")
        except Exception as e:
            logger.error(f"Error starting the API: {e}")