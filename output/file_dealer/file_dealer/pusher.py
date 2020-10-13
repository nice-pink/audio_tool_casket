import socket
import time
from file_dealer.lib.utils.log import Log
from typing import Optional


# Network client
class Pusher:
    
    def __init__(self, block_size: int = 1024):
        self.block_size = block_size
        self.socket = None
        self.is_connected = False

    def connect(self, address: str, port: int, timeout: Optional[float] = None):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(timeout)
            self.socket.connect(address, port)
            self.is_connected = True
        except Exception as exception:
            Log.error("Connect error: ", exception)

    def send(self, data: bytearray):
        if not self.is_connected:
            Log.warning("Error: Socket is not connected.")
            return False
        
        try:
            self.socket.sendall(data)
        except Exception as exception:
            Log.error('Send error:', str(exception))
            self.is_connected = False
            return False
        
        return True

    def send_file(self, file_path: str):
        if not self.is_connected:
            Log.warning("Error: Socket is not connected.")
            return
        
        with open(file_path, 'rb') as file:
            bytes_sent = self.send_line_by_line(file)
        
        return bytes_sent

    def send_line_by_line(self, file):
        bytes_sent = 0
        while True:
            line = file.read(self.block_size)
            if not line:
                break
            bytes_sent += len(line)
            
            try:
                self.socket.send(line)
            except IOError as io_error:
                Log.error('IOError:', io_error)
                break
            except Exception as exception:
                Log.error("Socket sent exception:", exception)
                break
            #time.sleep(0.02)
        return bytes_sent

    def receive(self):
        if not self.is_connected:
            Log.warning("Error: Socket is not connected.")
            return
        
        try:
            data = self.socket.recv(self.block_size)
        except IOError as io_error:
            Log.error('IOError:', io_error)
            return None
        except Exception as exception:
            Log.error("Socket receive exception:", exception)
            return None
        
        return data

    def close(self):
        try:
            self.socket.shutdown(2)
            self.socket.close()
        except Exception as e:
            Log.error("Socket shutdown exception:", e)

    def send_headers(self, method, optional=""):
        first_line = "{0} /stream HTTP/1.1 {1}\r\n\r\n".format(method, optional)
        try:
            self.socket.send(first_line.encode('utf-8'))
        except Exception as excpetion:
            Log.error("Send header exception:", excpetion)

    def get_is_connected(self):
        return self.is_connected