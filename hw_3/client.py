import socket
import threading

PORT = 50053

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def read_messages(session_name, user_name):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(('localhost', PORT))

        sock.send("read".encode())
        amount_received = 0
        while amount_received < len("read"):
            data = sock.recv(1024)
            amount_received += len(data)

        sock.send(session_name.encode())
        amount_received = 0
        while amount_received < len(session_name):
            data = sock.recv(1024)
            amount_received += len(data)

        sock.send(user_name.encode())
        amount_received = 0
        while amount_received < len(user_name):
            data = sock.recv(1024)
            amount_received += len(data)
        print("read fully connected")

        while True:
            data = sock.recv(1024)
            if data:
                print(bcolors.BOLD + bcolors.OKBLUE + data.decode() + bcolors.ENDC + bcolors.ENDC)
                sock.send(data)
            else:
                continue

def write_messages(session_name, user_name):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(('localhost', PORT))

        sock.send("write".encode())
        amount_received = 0
        while amount_received < len("write"):
            data = sock.recv(1024)
            amount_received += len(data)

        sock.send(session_name.encode())
        amount_received = 0
        while amount_received < len(session_name):
            data = sock.recv(1024)
            amount_received += len(data)

        sock.send(user_name.encode())
        amount_received = 0
        while amount_received < len(user_name):
            data = sock.recv(1024)
            amount_received += len(data)
        print("write fully connected")

        while True:
            message = input()
            sock.send(message.encode())
            amount_received = 0
            while amount_received < len(message):
                data = sock.recv(1024)
                amount_received += len(data)
            print(bcolors.BOLD + bcolors.OKGREEN + message + bcolors.ENDC + bcolors.ENDC)

def start():
    print("Enter name of session you want to connect to")
    session_name = input()
    print("Enter your username")
    user_name = input()

    threading.Thread(target=read_messages, args=(session_name, user_name)).start()
    threading.Thread(target=write_messages, args=(session_name, user_name)).start()

start()