from socket import *
import socket
import threading
import logging
import time
import sys
from concurrent.futures import ProcessPoolExecutor


from file_protocol import  FileProtocol
fp = FileProtocol()


def ProcessTheClient(conn):
    data_buffer = b""
    while True:
        received = conn.recv(65536)
        if received:
            data_buffer += received
            if b"\r\n\r\n" in data_buffer:
                break
        else:
            break
    if data_buffer:
        request_str = data_buffer.decode()
        response = fp.proses_string(request_str) + "\r\n\r\n"
        conn.sendall(response.encode())
    conn.close()

class Server(threading.Thread):
    def __init__(self, ipaddress='0.0.0.0', port=8889, max_workers=50):
        self.ipinfo = (ipaddress, port)
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.executor = ProcessPoolExecutor(max_workers=max_workers)
        threading.Thread.__init__(self)

    def run(self):
        logging.warning(f"server berjalan di ip address {self.ipinfo}")
        self.my_socket.bind(self.ipinfo)
        self.my_socket.listen(100)
        try:
            while True:
                conn, client_addr = self.my_socket.accept()
                logging.warning(f"connection from {client_addr}")
                self.executor.submit(ProcessTheClient, conn)
        except Exception as err:
            logging.warning(f"server stopped: {err}")

def main():
    svr = Server()
    svr.start()
    svr.join()


if __name__ == "__main__":
    main()