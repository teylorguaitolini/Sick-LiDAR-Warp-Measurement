from config import Config
from app import App

if __name__ == "__main__":
    conf = Config()
    app = App(conf)
    
    try:
        app.start()
    except KeyboardInterrupt:
        # Tratamento de interrupção pelo usuário (Ctrl+C)
        print("Programa interrompido pelo usuário.")
    finally:
        app.end()
