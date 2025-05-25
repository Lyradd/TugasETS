import json
import logging
import shlex
import base64

from file_interface import FileInterface

"""
* class FileProtocol bertugas untuk memproses 
data yang masuk, dan menerjemahkannya apakah sesuai dengan
protokol/aturan yang dibuat

* data yang masuk dari client adalah dalam bentuk bytes yang 
pada akhirnya akan diproses dalam bentuk string

* class FileProtocol akan memproses data yang masuk dalam bentuk
string
"""


class FileProtocol:
    def __init__(self):
        self.file = FileInterface()
    def proses_string(self, string_datamasuk=''):
        logging.warning(f"string diproses: {string_datamasuk}")
        try:
            string_datamasuk = string_datamasuk.strip()
            if not string_datamasuk:
                return json.dumps({'status': 'ERROR', 'data': 'Empty request'})
            # Ambil command di depan
            cmd, *rest = string_datamasuk.split(' ', 1)
            c_request = cmd.strip().lower()
            params = []
            if c_request == 'upload':
                # UPLOAD <filename> <base64...>
                if rest:
                    filename_and_data = rest[0]
                    filename, _, filedata = filename_and_data.partition(' ')
                    if filename and filedata:
                        params = [filename, filedata]
                    else:
                        return json.dumps({'status': 'ERROR', 'data': 'Invalid upload format'})
                else:
                    return json.dumps({'status': 'ERROR', 'data': 'Invalid upload format'})
            elif rest:
                # Untuk GET, DELETE, dll: hanya satu parameter
                params = [rest[0].strip()]
            # Untuk LIST, params tetap []
            logging.warning(f"memproses request: {c_request}")
            logging.warning(f"Params: {params}")
            cl = getattr(self.file, c_request)(params)
            return json.dumps(cl)
        except Exception as e:
            logging.warning(f"Exception: {e}")
            return json.dumps({'status': 'ERROR', 'data': 'request tidak dikenali'})


if __name__=='__main__':
    fp = FileProtocol()
    print(fp.proses_string("LIST"))
    
    encoded = base64.b64encode(b'goodmorning').decode()
    print(fp.proses_string(f'UPLOAD testfile.txt {encoded}'))