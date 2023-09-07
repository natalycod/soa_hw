import socket
import threading
import sys

import grpc
import mafia_pb2
import mafia_pb2_grpc
from concurrent.futures import ThreadPoolExecutor
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
        sock.connect(('server', PORT))

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
        sock.connect(('server', PORT))

        send_text(sock, "write")
        send_text(sock, session_name)
        send_text(sock, user_name)

        print("write fully connected")

        while True:
            message = input()
            send_text(sock, message)

class UserSession:
    def __init__(self, executor, channel, session_name, user_name, users_count):
        self.session_name = session_name
        self.user_name = user_name
        self.connected = False
        self.users_count = users_count

        self._executor = executor
        self._channel = channel
        self._consumer_future = None
        self._stub = mafia_pb2_grpc.MafiaStub(self._channel)
        self._queue = Queue()

        queue = Queue()
        threading.Thread(target=self.listen_for_messages, daemon=False, args=[]).start()
        threading.Thread(target=self.process_user_commands, daemon=False, args=[]).start()
        session_id = queue.get()

    def listen_for_messages(self):
        response = self._stub.ConnectToServer(mafia_pb2.ConnectToServerMessage(session_name=self.session_name, user_name=self.user_name, users_count=self.users_count))
        if response.HasField("common_error"):
            print("error: " + response.common_error.error_text)

        while True:
            response = self._stub.GetNewMessage(mafia_pb2.GetMessageRequest(session_name=self.session_name, user_name=self.user_name))
            if response.HasField("server_message"):
                if response.server_message.major_type:
                    print(bcolors.OKBLUE + response.server_message.text + bcolors.ENDC)
                else:
                    print(bcolors.OKCYAN + response.server_message.text + bcolors.ENDC)
            if response.HasField("user_message"):
                if response.user_message.major_type:
                    print(bcolors.BOLD + bcolors.OKGREEN + response.user_message.user_name + ": " + response.user_message.text + bcolors.ENDC + bcolors.ENDC)
                else:
                    print(bcolors.OKGREEN + response.user_message.user_name + ": " + response.user_message.text + bcolors.ENDC)

    def _handle_common_response_error(self, resp):
        if resp.HasField("common_error"):
            print(bcolors.FAIL + "error: " + resp.common_error.error_text + bcolors.ENDC)

    def process_user_commands(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(('server', PORT))

            send_text(sock, "write")
            send_text(sock, session_name)
            send_text(sock, user_name)

            print("write fully connected")

            while True:
                command = input()
                if command.startswith("chat "):
                    send_text(sock, command[5:])
                if command == "end_day":
                    response = self._stub.EndDay(mafia_pb2.EndDayRequest(session_name=self.session_name, user_name=self.user_name))
                    self._handle_common_response_error(response)
                if command.startswith("check "):
                    response = self._stub.CheckUser(mafia_pb2.CheckUserRequest(session_name=self.session_name, user_name=self.user_name, check_name=command[6:]))
                    self._handle_common_response_error(response)
                if command.startswith("kill "):
                    response = self._stub.KillUser(mafia_pb2.KillUserRequest(session_name=self.session_name, user_name=self.user_name, kill_name=command[5:]))
                    self._handle_common_response_error(response)
                if command == "publish":
                    response = self._stub.Publish(mafia_pb2.PublishRequest(session_name=self.session_name, user_name=self.user_name))
                    self._handle_common_response_error(response)
                if command.startswith("blame "):
                    response = self._stub.Blame(mafia_pb2.BlameRequest(session_name=self.session_name, user_name=self.user_name, blame_name=command[6:]))
                    self._handle_common_response_error(response)
                if command == "help":
                    response = self._stub.Help(mafia_pb2.HelpRequest())
                    for command in response.commands:
                        print(bcolors.WARNING + bcolors.BOLD + command.command + ": " + bcolors.ENDC + bcolors.WARNING + command.explanation + bcolors.ENDC)

if len(sys.argv) < 3:
    print(bcolors.FAIL + "Please run the command with 2 additional parameters in this order:" + bcolors.ENDC)
    print(bcolors.OKBLUE + bcolors.BOLD + "session_name (required):" + bcolors.ENDC + bcolors.OKBLUE + "name of session you want to connect to" + bcolors.ENDC)
    print(bcolors.OKBLUE + bcolors.BOLD + "user_name (required):" + bcolors.ENDC + bcolors.OKBLUE + "your nickname in game" + bcolors.ENDC)
    exit(0)

session_name = sys.argv[1]
user_name = sys.argv[2]
users_count = 0
if len(sys.argv) >= 4:
    users_count = int(sys.argv[3])
users_count = max(users_count, 4)

threading.Thread(target=read_messages, args=(session_name, user_name)).start()

with grpc.insecure_channel("mafia_server:50051") as channel:
    executor = ThreadPoolExecutor()
    user_session = UserSession(executor, channel, session_name, user_name, users_count)
