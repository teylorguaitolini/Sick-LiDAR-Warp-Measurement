import serial
from utils.logger_config import logger

class ESP32Serial:
    def __init__(self, port, baudrate=115200, timeout=1):
        """
        Initializes the serial connection with ESP32.

        :param port: Serial port to which ESP32 is connected.
        :param baudrate: Baud rate for transmission (default: 115200).
        :param timeout: Timeout for reading in seconds (default: 1).
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.connection = None

    def connect(self):
        """Establishes the serial connection."""
        try:
            self.connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            logger.info(f"Connected to {self.port} at {self.baudrate} baud.")
        except serial.SerialException as e:
            raise Exception(f"Error connecting to port {self.port}: {e}")

    def disconnect(self):
        """Closes the serial connection."""
        if self.connection and self.connection.is_open:
            self.connection.close()
            logger.info(f"Disconnected from {self.port}.")

    def send_command(self, command):
        """
        Sends a command via serial to ESP32.

        :param command: Command to be sent.
        """
        if self.connection and self.connection.is_open:
            command_str = command + '\n'  # Adds a new line to the command
            self.connection.write(command_str.encode('utf-8'))
            logger.info(f"Command '{command}' sent.")
        else:
            raise Exception("Serial connection is not open.")

    def read_response(self):
        """Reads the response from the serial connection."""
        if self.connection and self.connection.is_open:
            response = self.connection.readline().decode('utf-8').strip()
            return response
        else:
            raise Exception("Serial connection is not open.")
