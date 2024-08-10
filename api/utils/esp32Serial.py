import serial

class ESP32Serial:
    def __init__(self, port, baudrate=115200, timeout=1):
        """
        Inicializa a conexão serial com o ESP32.

        :param port: Porta serial à qual o ESP32 está conectado.
        :param baudrate: Taxa de transmissão em bauds (padrão: 115200).
        :param timeout: Tempo limite para leitura em segundos (padrão: 1).
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.connection = None
        self.conn_sts = False

    @property
    def is_connected(self):
        """Verifica se a conexão serial está aberta."""
        return self.conn_sts

    def connect(self):
        """Estabelece a conexão serial."""
        try:
            self.connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            print(f"Conectado ao {self.port} a {self.baudrate} baud.")
            self.conn_sts = True
        except serial.SerialException as e:
            print(f"Erro ao conectar na porta {self.port}: {e}")

    def disconnect(self):
        """Fecha a conexão serial."""
        if self.connection and self.connection.is_open:
            self.connection.close()
            print(f"Desconectado de {self.port}.")

    def send_command(self, command):
        """
        Envia um comando via serial para o ESP32.

        :param command: Comando a ser enviado.
        """
        if self.connection and self.connection.is_open:
            command_str = command + '\n'  # Adiciona uma nova linha ao comando
            self.connection.write(command_str.encode('utf-8'))
            print(f"Comando '{command}' enviado.")
        else:
            print("Conexão serial não está aberta.")

    def read_response(self):
        """Lê a resposta da conexão serial."""
        if self.connection and self.connection.is_open:
            response = self.connection.readline().decode('utf-8').strip()
            return response
        return None

    def __enter__(self):
        """Suporte ao gerenciamento de contexto (with statement)."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Fecha a conexão ao sair do contexto."""
        self.disconnect()
