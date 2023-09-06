import socket
import threading

import grpc
import mafia_pb2
import mafia_pb2_grpc
from concurrent.futures import ThreadPoolExecutor

PORT = 50052

current_sessions = {}

def send_message(sock, message):
    sock.send(message.encode())
    amount_received = 0
    while amount_received < len(message):
        data = sock.recv(1024)
        amount_received += len(data)

class ChatSession:
    def __init__(self, session_name):
        self.users = {}
        self.session_name = session_name

    def get_chat_receivers(self, user_name):
        try:
            with grpc.insecure_channel("localhost:50051") as channel:
                executor = ThreadPoolExecutor()
                stub = mafia_pb2_grpc.MafiaStub(channel)
                resp = stub.ChatReceivers(mafia_pb2.ChatReceiversRequest(session_name=self.session_name, user_name=user_name))
                if not resp.in_game:
                    return self.users.keys()
                result = []
                for receiver in resp.receivers:
                    if receiver in self.users:
                        result.append(receiver)
                return result
        except:
            return self.users.keys()

    def add_user(self, user_name, connection_type, connection):
        if user_name not in self.users:
            self.users[user_name] = {}
        self.users[user_name][connection_type] = connection
        if len(self.users[user_name]) == 2:
            for user, connections in self.users.items():
                send_message(connections["read"], "new_connection")
                send_message(connections["read"], user_name)
                send_message(connections["read"], ", ".join(self.users.keys()))

    def send_all(self, user_name, message):
        receivers = self.get_chat_receivers(user_name)
        for user in receivers:
            send_message(self.users[user]["read"], "new_message")
            send_message(self.users[user]["read"], user_name)
            send_message(self.users[user]["read"], message)

class ChatConnection:
    def __init__(self, connection):
        self.connection = connection

        connection_type = connection.recv(1024).decode()
        self.connection_type = connection_type
        connection.send(connection_type.encode())

        session_name = connection.recv(1024).decode()
        self.session_name = session_name
        connection.send(session_name.encode())

        user_name = connection.recv(1024).decode()
        self.user_name = user_name
        connection.send(user_name.encode())

        if self.session_name not in current_sessions:
            current_sessions[self.session_name] = ChatSession(self.session_name)
        self.session = current_sessions[self.session_name]
        self.session.add_user(self.user_name, self.connection_type, self.connection)

        if self.connection_type == "write":
            threading.Thread(target=self._listen_to_messages, args=()).start()

    def _listen_to_messages(self):
        while True:
            data = self.connection.recv(1024).decode()
            if data:
                self.session.send_all(self.user_name, data)
                self.connection.send(data.encode())

class ChatServer:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('0.0.0.0', PORT))
        self.sock.listen()
        print("Started server on port", PORT)
        self._listen_to_new_connections()

    def _listen_to_new_connections(self):
        while True:
            connection, addr = self.sock.accept()
            connection = ChatConnection(connection)

chat_connection = ChatServer()