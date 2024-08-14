import uvicorn
from utils import ESP32Serial, Config, logger
from fastapi import FastAPI
from datetime import datetime

class API:
    def __init__(self, conf: Config):
        self.conf = conf

        self.esp32 = ESP32Serial(port=conf.com_port, baudrate=conf.baud_rate, timeout=conf.timeout)

        self.app = FastAPI()

        @self.app.post("/start")
        def motor_start():
            try:
                logger.info("Starting request received.")
                self.esp32.send_command("start")

                start_time = datetime.now()
                while True:
                    if (datetime.now() - start_time).seconds >= self.conf.timeout:
                        raise TimeoutError("Timeout in motor start response.")

                    response = self.esp32.read_response()
                    if response == "starting":
                        logger.info("Motor is starting.")
                        break

                return {"message": "running"}
            except Exception as e:
                logger.error(f"Error starting motor: {e}")
                return {"message": "error"}
            
    def start(self):
        try:
            self.esp32.connect()
            logger.info("ESP32 is connected.")
            
            uvicorn.run(
                self.app, 
                host=self.conf.host, 
                port=self.conf.port,
                log_config=None
            )
        except KeyboardInterrupt:
            logger.info("The API was finished by a KeyboardInterrupt.")
        except Exception as e:
            logger.error(f"Error starting the API: {e}")
        finally:
            self.esp32.disconnect()
            logger.info("ESP32 is disconnected.")
        