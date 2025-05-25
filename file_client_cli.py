import os
import socket
import json
import base64
import logging

server_address = ('0.0.0.0', 7777)

def send_command(command_str=""):
    global server_address
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    logging.warning(f"connecting to {server_address}")
    try:
        logging.warning(f"sending message ")
        command_str = command_str + "\r\n\r\n"
        sock.sendall(command_str.encode())
        # Look for the response, waiting until socket is done (no more data)
        data_received="" #empty string
        while True:
            #socket does not receive all data at once, data comes in part, need to be concatenated at the end of process
            data = sock.recv(16)
            if data:
                #data is not empty, concat with previous content
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            else:
                # no more data, stop the process by break
                break
        # at this point, data_received (string) will contain all data coming from the socket
        # to be able to use the data_received as a dict, need to load it using json.loads()
        hasil = json.loads(data_received)
        logging.warning("data received from server:")
        return hasil
    except:
        logging.warning("error during data receiving")
        return False

def remote_list():
    result = send_command("LIST")
    if result and result.get('status') == 'OK':
        print("File list:")
        for filename in result['data']:
            print(f"- {filename}")
        return True
    else:
        print("Failed to retrieve file list")
        return False

def remote_get(filename=""):
    result = send_command(f"GET {filename}")
    if result and result.get('status') == 'OK':
        file_name = result['data_namafile']
        file_content = base64.b64decode(result['data_file'])
        with open(file_name, 'wb') as f:
            f.write(file_content)
        return True
    else:
        print("Failed to download file")
        return False

def remote_upload(filepath=""):
    if not os.path.isfile(filepath):
        logging.warning("File not found")
        return False
    with open(filepath, "rb") as f:
        encoded_content = base64.b64encode(f.read()).decode()
    command = f"UPLOAD {os.path.basename(filepath)} {encoded_content}"
    result = send_command(command)
    if result and result.get('status') == 'OK':
        print(result['data'])
        return True
    else:
        print(result['data'] if result else "Upload failed")
        return False

def remote_delete(filename=""):
    result = send_command(f"DELETE {filename}")
    if result and result.get('status') == 'OK':
        print(result['data'])
        return True
    else:
        print(result['data'] if result else "Delete failed")
        return False

if __name__ == '__main__':
    server_address = ('172.16.16.101', 8889)
    remote_upload('donalbebek.jpg')
    remote_upload('rfc2616.pdf')
    remote_upload('pokijan.jpg')
    remote_get('donalbebek.jpg')
    remote_delete('pokijan.jpg')
    remote_delete('rfc2616.pdf')
    remote_delete('donalbebek.jpg')
    remote_list()