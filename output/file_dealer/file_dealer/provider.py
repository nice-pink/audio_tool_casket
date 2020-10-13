from file_dealer.lib.utils.log import Log
import socket
from time import sleep

class Provider:

    def __init__(self, target: str, port: int, block_size: int = 1024):
        self.block_size = block_size
        self.socket = None
        self.connection = None
        self.address = None
        self.__setup_server(target, port)

    def provide_files(self, filenames: [], packet_delay: float = 0):
        if not self.connection:
            Log.error('No connection')
            return

        for filename in filenames:
            with open(filename, 'rb') as file:
                self.__send_file(file)
            sleep(packet_delay)

    # def provide(self, packets: []):
    #     print('provide byte packets')    

    # Server

    def __setup_server(self, target: str, port: int):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(None)
            self.socket.bind((target, port))
            self.socket.listen()
            self.connection, self.address = self.socket.accept()
        except Exception as exception:
            Log.error('Connect error:', exception)

    def __send_file(self, file):
        line = file.read(self.block_size)
        while line:
            self.connection.sendall(line)
            line = file.read(self.block_size)
