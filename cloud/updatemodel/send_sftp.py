import paramiko
import time
import argparse
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

def main():
    parser = argparse.ArgumentParser(description='Send a file over SFTP.')
    parser.add_argument('--server', type=str, default='10.8.108.245', help='IP address of the SFTP server (default: 10.8.108.245)')
    parser.add_argument('--filename', type=str, default='yolo.onnx', help='Name of the file to send')
    
    # These could be made into optional arguments with default values if needed
    parser.add_argument('--port', type=int, default=22, help='Port of the SFTP server (default: 22)')
    parser.add_argument('--username', type=str, default='gamadita3', help='Username for SFTP login')
    parser.add_argument('--password', type=str, default='gamadita3', help='Password for SFTP login')
    parser.add_argument('--remote_path', type=str, default='/home/gamadita3/Tesis/CODE/model/', help='Remote directory path to upload the file')

    args = parser.parse_args()

    # Build local and remote file paths
    local_file_path = args.filename
    remote_file_path = args.remote_path + args.filename

    # Call the SFTP function
    sftp_send_file(args.server, args.port, args.username, args.password, local_file_path, remote_file_path)

if __name__ == "__main__":
    main()