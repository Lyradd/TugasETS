import os
import base64
from glob import glob


class FileInterface:
    def __init__(self):
        os.chdir('files/')

    def list(self, params=[]):
        try:
            files = glob('*.*')
            return {'status': 'OK', 'data': files}
        except Exception as err:
            return {'status': 'ERROR', 'data': str(err)}

    def upload(self, params=[]):
        try:
            filename = params[0]
            encoded_data = params[1]
            file_bytes = base64.b64decode(encoded_data)
            with open(filename, 'wb') as file:
                file.write(file_bytes)
            return {'status': 'OK', 'data': f'{filename} uploaded successfully'}
        except Exception as err:
            return {'status': 'ERROR', 'data': str(err)}

    def get(self, params=[]):
        try:
            filename = params[0]
            if not filename or not os.path.exists(filename):
                return {'status': 'ERROR', 'data': 'File not found'}
            with open(filename, 'rb') as file:
                encoded = base64.b64encode(file.read()).decode()
            return {'status': 'OK', 'data_namafile': filename, 'data_file': encoded}
        except Exception as err:
            return {'status': 'ERROR', 'data': str(err)}

    def delete(self, params=[]):
        try:
            filename = params[0]
            if not os.path.exists(filename):
                return {'status': 'ERROR', 'data': 'File not found'}
            os.remove(filename)
            return {'status': 'OK', 'data': f'{filename} deleted successfully'}
        except Exception as err:
            return {'status': 'ERROR', 'data': str(err)}

if __name__ == '__main__':
    f = FileInterface()
    print(f.list())
    # print(f.get(['pokijan.jpg']))
    # print(f.upload(['test22.txt','aGVsbG8=']))