import socket
import threading
import sys
from queue import Queue

PORT = 50052

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

queue_read = Queue()
queue_write = Queue()

def read_messages_to_queue():
    while True:
        message = input()
        queue_read.put(message)

def write_messages_from_queue():
    while True:
        if not queue_write.empty():
            message = queue_write.get()
            print(message)


class Message:
    def __init__(self):
        pass

class ChatSession:
    def __init__(self, session_name, user_name):
        self.session_name = session_name
        self.user_name = user_name
        
        threading.Thread(target=self.read_messages, args=()).start()
        threading.Thread(target=self.write_messages, args=()).start()

    def read_one_message(self, sock):
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

    def send_text(self, sock, text):
        sock.send(text.encode())
        amount_received = 0
        while amount_received < len(text):
            data = sock.recv(1024)
            amount_received += len(data)

    def write_messages(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(('server', PORT))

            self.send_text(sock, "write")
            self.send_text(sock, self.session_name)
            self.send_text(sock, self.user_name)

            print("write fully connected")

            while True:
                if not queue_read.empty():
                    message = queue_read.get()
                    self.send_text(sock, message)

    def read_messages(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(('server', PORT))

            self.send_text(sock, "read")
            self.send_text(sock, self.session_name)
            self.send_text(sock, self.user_name)

            print("read fully connected")

            while True:
                message = self.read_one_message(sock)
                if message.type == "new_message":
                    queue_write.put(message.user + ": " + message.text)
                elif message.type == "new_connection":
                    queue_write.put("New user connected: " + message.user)

if len(sys.argv) < 3:
    print(bcolors.FAIL + "Please run the command with 2 additional parameters in this order:" + bcolors.ENDC)
    print(bcolors.OKBLUE + bcolors.BOLD + "session_name (required):" + bcolors.ENDC + bcolors.OKBLUE + "name of session you want to connect to" + bcolors.ENDC)
    print(bcolors.OKBLUE + bcolors.BOLD + "user_name (required):" + bcolors.ENDC + bcolors.OKBLUE + "your nickname in game" + bcolors.ENDC)
    exit(0)

session_name = sys.argv[1]
user_name = sys.argv[2]

session = ChatSession(session_name, user_name)

threading.Thread(target=read_messages_to_queue, args=()).start()
threading.Thread(target=write_messages_from_queue, args=()).start()
