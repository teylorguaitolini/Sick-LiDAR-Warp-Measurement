import sys
import uvicorn
from config.config import Config
from app.app import App
from app.api import Api

if __name__ == "__main__":
    """
    Manage the flow of execution.

    bash: python src/main.py api - to execute the API

    bash: python src/main.py - to execute the APP
    """
    conf = Config()

    if len(sys.argv) > 1 and sys.argv[1] == "api":
        api = Api(conf)
        uvicorn.run(api.app, host="0.0.0.0", port=8000)
    else:
        app = App(conf)
        app.start()
