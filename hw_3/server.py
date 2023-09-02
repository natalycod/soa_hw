import socket
import threading

PORT = 50053

current_sessions = {}

class ChatSession:
    def __init__(self):
        self.users = {}
    
    def add_user(self, user_name, connection_type, connection):
        if user_name not in self.users:
            self.users[user_name] = {}
        self.users[user_name][connection_type] = connection
        print("got connection for", user_name, ":", connection_type)
    
    def send_all(self, user_name, message):
        for user, connections in self.users.items():
            if user != user_name:
                connections["read"].send((user_name + ": " + message).encode())

class ChatConnection:
    def __init__(self, connection):
        self.connection = connection

        connection.send("here".encode())

        connection_type = connection.recv(1024)
        self.connection_type = connection_type.decode()
        print("received type:", connection_type.decode())
        connection.send(connection_type)

        session_name = connection.recv(1024)
        self.session_name = session_name.decode()
        print("received session:", session_name.decode())
        connection.send(session_name)

        user_name = connection.recv(1024)
        self.user_name = user_name.decode()
        print("received user:", user_name.decode())
        connection.send(user_name)

        print("started", session_name, user_name)

        if self.session_name not in current_sessions:
            current_sessions[self.session_name] = ChatSession()
        self.session = current_sessions[self.session_name]
        self.session.add_user(self.user_name, self.connection_type, self.connection)

        if self.connection_type == "write":
            threading.Thread(target=self._listen_to_messages, args=()).start()

    def _listen_to_messages(self):
        while True:
            data = self.connection.recv(1024)
            if data:
                print("received:", data.decode())
                self.session.send_all(self.user_name, data.decode())
                self.connection.send(data)

class ChatServer:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('localhost', PORT))
        self.sock.listen()
        print("Started server on port", PORT)
        self._listen_to_new_connections()

    def _listen_to_new_connections(self):
        while True:
            connection, addr = self.sock.accept()
            print("Connection from", addr)

            connection = ChatConnection(connection)

chat_connection = ChatServer()
