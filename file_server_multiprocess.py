from socket import *
import socket
import threading
import logging
from concurrent.futures import ProcessPoolExecutor
from file_protocol import FileProtocol

fp = FileProtocol()

def handle_client(conn):
    data_buffer = b""
    while True:
        chunk = conn.recv(65536)
        if chunk:
            data_buffer += chunk
            if b"\r\n\r\n" in data_buffer:
                break
        else:
            break
    if data_buffer:
        request = data_buffer.decode()
        response = fp.proses_string(request) + "\r\n\r\n"
        conn.sendall(response.encode())
    conn.close()

class MultiProcessServer(threading.Thread):
    def __init__(self, host='0.0.0.0', port=8889, max_workers=50):
        super().__init__()
        self.address = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.executor = ProcessPoolExecutor(max_workers=max_workers)

    def run(self):
        logging.warning(f"server berjalan di ip address {self.address}")
        self.sock.bind(self.address)
        self.sock.listen(100)
        try:
            while True:
                conn, client_addr = self.sock.accept()
                logging.warning(f"connection from {client_addr}")
                self.executor.submit(handle_client, conn)
        except Exception as err:
            logging.warning(f"server stopped: {err}")

def main():
    server = MultiProcessServer()
    server.start()
    server.join()

if __name__ == "__main__":
    main()
