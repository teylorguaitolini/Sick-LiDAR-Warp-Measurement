import uvicorn
from time import sleep
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
        
        @self.app.get("/results")
        def get_results():
            logger.info("Results request received.")
            
            return {
                "warping": self.measure.warping,
                "length": self.measure.lenght,
                "height": self.measure.hight,
                "distance": self.measure.distance,
                "warping_image": f"{self.measure.warping_image}"
            }


    def start(self):
        try:
            uvicorn.run(
                self.app, 
                host="0.0.0.0", # localhost
                port=self.conf.API_port,
                log_config=None
            )
        except KeyboardInterrupt:
            logger.info("The API was finished by a KeyboardInterrupt.")
        except Exception as e:
            logger.error(f"Error starting the API: {e}")