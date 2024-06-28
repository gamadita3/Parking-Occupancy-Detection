import paramiko
import time
from os.path import basename

def sftp_send_file(server, port, username, password, local_path, remote_path):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port=port, username=username, password=password)

    sftp = client.open_sftp()
    start_time = time.time()
    sftp.put(local_path, remote_path)
    sftp.close()
    client.close()
    end_time = time.time()
    
    print(f"SFTP transfer completed in {end_time - start_time} seconds")

# Usage example
sftp_send_file('10.8.108.245', 22, 'gamadita3', 'gamadita3', 'yolo.onnx', '/home/gamadita3/Tesis/CODE/model/yolo.onnx')
