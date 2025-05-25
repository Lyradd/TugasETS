from socket import *
import socket
import logging
import time
import sys
from concurrent.futures import ThreadPoolExecutor

from file_protocol import FileProtocol
fp = FileProtocol()

def process_client(conn, addr):
    buffer = ""
    while True:
        data = conn.recv(65536)
        if data:
            buffer += data.decode()
            if "\r\n\r\n" in buffer:
                break
        else:
            break
    if buffer:
        reply = fp.proses_string(buffer) + "\r\n\r\n"
        conn.sendall(reply.encode())
    conn.close()

class Server:
    def __init__(self, ipaddress='0.0.0.0', port=8889, max_workers=10):
        self.ipinfo = (ipaddress, port)
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def run(self):
        logging.warning(f"server berjalan di ip address {self.ipinfo}")
        self.my_socket.bind(self.ipinfo)
        self.my_socket.listen(5)
        while True:
            conn, client_addr = self.my_socket.accept()
            logging.warning(f"connection from {client_addr}")
            self.executor.submit(process_client, conn, client_addr)

def main():
    svr = Server()
    svr.run()

if __name__ == "__main__":
    main()
