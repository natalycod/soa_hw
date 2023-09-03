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

class Message:
    def __init__(self):
        pass

def read_one_message(sock):
    message = Message()
    message.type = None
    while not message.type:
        message.type = sock.recv(1024).decode()
        sock.send(message.type.encode())

    if message.type in ["new_message", "new_connection"]:
        message.user = None
        while not message.user:
            message.user = sock.recv(1024).decode()
            sock.send(message.user.encode())

    if message.type in ["new_message"]:
        message.text = None
        while not message.text:
            message.text = sock.recv(1024).decode()
            sock.send(message.text.encode())
    
    if message.type in ["new_connection"]:
        message.users = None
        while not message.users:
            message.users = sock.recv(1024).decode()
            sock.send(message.users.encode())

    return message

def send_text(sock, text):
    sock.send(text.encode())
    amount_received = 0
    while amount_received < len(text):
        data = sock.recv(1024)
        amount_received += len(data)

def read_messages(session_name, user_name):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(('localhost', PORT))

        send_text(sock, "read")
        send_text(sock, session_name)
        send_text(sock, user_name)

        print("read fully connected")

        while True:
            message = read_one_message(sock)
            if message.type == "new_message":
                print(bcolors.BOLD + bcolors.OKGREEN + message.user + ": " + message.text + bcolors.ENDC + bcolors.ENDC)
            elif message.type == "new_connection":
                print(bcolors.BOLD + bcolors.OKBLUE + "New user connected: " + message.user + bcolors.ENDC + bcolors.ENDC)
                print(bcolors.BOLD + bcolors.OKBLUE + "Current users: " + message.users + bcolors.ENDC + bcolors.ENDC)

def write_messages(session_name, user_name):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(('localhost', PORT))

        send_text(sock, "write")
        send_text(sock, session_name)
        send_text(sock, user_name)

        print("write fully connected")

        while True:
            message = input()
            send_text(sock, message)

def start():
    print("Enter name of session you want to connect to")
    session_name = input()
    print("Enter your username")
    user_name = input()

    threading.Thread(target=read_messages, args=(session_name, user_name)).start()
    threading.Thread(target=write_messages, args=(session_name, user_name)).start()

start()
