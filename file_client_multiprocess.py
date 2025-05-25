import os
import socket
import json
import base64
import logging
import concurrent.futures
import time

server_address = ('0.0.0.0', 7777)

def send_command(cmd):
    global server_address
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    logging.warning(f"connecting to {server_address}")
    try:
        logging.warning("sending message")
        cmd = cmd + "\r\n\r\n"
        sock.sendall(cmd.encode())
        response = ""
        while True:
            chunk = sock.recv(65536)
            if chunk:
                response += chunk.decode()
                if "\r\n\r\n" in response:
                    break
            else:
                break
        result = json.loads(response)
        logging.warning("data received from server:")
        return result
    except Exception:
        logging.warning("error during data receiving")
        return False

def remote_list():
    res = send_command("LIST")
    if res and res.get('status') == 'OK':
        print("daftar file : ")
        for fname in res['data']:
            print(f"- {fname}")
        return True
    else:
        print("Gagal")
        return False

def remote_get(filename):
    res = send_command(f"GET {filename}")
    if res and res.get('status') == 'OK':
        fname = res['data_namafile']
        content = base64.b64decode(res['data_file'])
        with open(fname, 'wb') as f:
            f.write(content)
        return True
    else:
        print("Gagal")
        return False

def remote_upload(filename):
    if not os.path.exists(filename):
        logging.warning("File does not exist")
        return False
    with open(filename, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    res = send_command(f"UPLOAD {filename} {encoded}")
    if res and res.get('status') == 'OK':
        print(res['data'])
        return True
    else:
        print(res['data'] if res else "Upload failed")
        return False

def remote_delete(filename):
    res = send_command(f"DELETE {filename}")
    if res and res.get('status') == 'OK':
        print(res['data'])
        return True
    else:
        print(res['data'] if res else "Delete failed")
        return False

def worker_task(worker_id, op, fname):
    start = time.perf_counter()
    if op == 'upload':
        result = remote_upload(fname)
    elif op == 'download':
        result = remote_get(fname)
    else:
        result = False
    end = time.perf_counter()
    file_size = os.path.getsize(fname) if os.path.exists(fname) else 0
    duration = end - start
    throughput = file_size / duration if duration > 0 and result else 0
    return {
        'worker_id': worker_id,
        'success': result,
        'duration': duration,
        'throughput': throughput
    }

def summarize_results(results, op, fname, no):
    total = len(results)
    success = sum(1 for r in results if r['success'])
    fail = total - success
    avg_time = sum(r['duration'] for r in results) / total if total else 0
    avg_tp = sum(r['throughput'] for r in results) / total if total else 0
    print(f"{no:<3}| {op:<8}| {fname:<15}| {total:<6}| {avg_time:<12.4f}| {avg_tp:<14.2f}| {success:<6}| {fail:<5}")

if __name__ == '__main__':
    import concurrent.futures
    import time
    server_address = ('172.16.16.101', 8889)

    # Daftar file yang tersedia
    test_files = [
        ('10mb_file', '10MB'),
        ('50mb_file', '50MB'),
        ('100mb_file', '100MB')
    ]
    file_dict = {label: fname for fname, label in test_files}
    file_labels = [label for _, label in test_files]
    operations = ['upload', 'download']

    print('Pilih operasi:')
    for i, op in enumerate(operations):
        print(f"{i+1}. {op}")
    op_idx = int(input('Masukkan nomor operasi: ')) - 1
    op = operations[op_idx]

    print('Pilih file:')
    for i, label in enumerate(file_labels):
        print(f"{i+1}. {label}")
    file_idx = int(input('Masukkan nomor file: ')) - 1
    label = file_labels[file_idx]
    fname = file_dict[label]

    nworker = int(input('Masukkan jumlah worker: '))

    print(f"No | Operasi | File         | Worker| Avg Waktu(s) | Avg Throughput | Sukses| Gagal")
    print('-'*75)
    no = 1
    try:
        def worker(worker_id):
            try:
                if op == 'upload':
                    upload_success = remote_upload(fname)
                    file_size = os.path.getsize(fname) if upload_success and os.path.exists(fname) else 0
                    return {
                        'worker_id': worker_id,
                        'success': upload_success,
                        'bytes': file_size if upload_success else 0
                    }
                elif op == 'download':
                    download_success = remote_get(fname)
                    file_size = os.path.getsize(fname) if download_success and os.path.exists(fname) else 0
                    return {
                        'worker_id': worker_id,
                        'success': download_success,
                        'bytes': file_size if download_success else 0
                    }
                else:
                    return {'worker_id': worker_id, 'success': False, 'bytes': 0}
            except Exception as e:
                return {'worker_id': worker_id, 'success': False, 'bytes': 0, 'error': str(e)}
        start_all = time.perf_counter()
        worker_success = 0
        worker_fail = 0
        total_bytes = 0
        with concurrent.futures.ProcessPoolExecutor(max_workers=nworker) as executor:
            futures = [executor.submit(worker, i+1) for i in range(nworker)]
            for future in concurrent.futures.as_completed(futures):
                try:
                    res = future.result()
                    if res['success']:
                        worker_success += 1
                        total_bytes += res['bytes']
                    else:
                        worker_fail += 1
                        if 'error' in res:
                            print(f"Worker {res['worker_id']} failed with error: {res['error']}")
                except Exception as e:
                    worker_fail += 1
                    print(f"Worker failed with exception: {e}")
        end_all = time.perf_counter()
        total_time = end_all - start_all
        throughput = total_bytes / total_time if total_time > 0 else 0
        avg_time = total_time / nworker if nworker > 0 else 0
        avg_tp = throughput / nworker if nworker > 0 else 0
        print(f"{no:<3}| {op:<8}| {label:<12}| {nworker:<6}| {avg_time:<12.4f}| {avg_tp:<14.2f}| {worker_success:<6}| {worker_fail:<5}")
        no += 1
    except Exception as e:
        print(f"[ERROR] Kombinasi {op}-{label}-{nworker} gagal: {e}. Lanjut ke proses berikutnya.")
        no += 1