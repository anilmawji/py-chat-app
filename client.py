import socket
import errno
import sys
import tkinter as tk
import threading

PORT = 1234
DEBUG_MODE = True
HEADER_LENGTH = 10
ENCODING = "UTF-8"


class ChatClient:
    def __init__(self, port, name='Unknown'):
        self.port = port
        self.name = name
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False

    def connect(self, server_address='127.0.0.1', port=PORT):
        try:
            self.port = int(port)
            self.socket.connect((server_address, self.port))
            self.socket.setblocking(False)
            self.connected = True

            name_data = self.name.encode(ENCODING)
            name_header = f"{len(name_data):<{HEADER_LENGTH}}".encode(ENCODING)
            self.socket.sendall(name_header + name_data)

            if DEBUG_MODE: print(f"[CONNECTED] you are now connected to {server_address}:{self.port}")

        except socket.error as e:
            if DEBUG_MODE: print("Socket error: {}".format(str(e)))
            sys.exit(1)

    def send_message(self, msg):
        if msg:
            msg_data = msg.encode(ENCODING)
            msg_header = f"{len(msg_data):<{HEADER_LENGTH}}".encode(ENCODING)
            self.socket.sendall(msg_header + msg_data)

    def receive_message(self):
        name_header = self.socket.recv(HEADER_LENGTH)

        if not len(name_header):
            if DEBUG_MODE: print("[DISCONNECTED] connection closed by server")
            sys.exit(0)

        name_length = int(name_header.decode(ENCODING).strip())
        name = self.socket.recv(name_length).decode(ENCODING)

        msg_header = self.socket.recv(HEADER_LENGTH)
        msg_length = int(msg_header.decode(ENCODING).strip())
        msg = self.socket.recv(msg_length).decode(ENCODING)
        print(self.format_message(name, msg))

        return self.format_message(name, msg)

    def format_message(self, name, msg):
        return name + ": " + msg

    def close(self):
        self.connected = False
        self.socket.close()

        if DEBUG_MODE: print(f"[DISCONNECTED] ended connection with server")

    def get_name(self):
        return self.name

    def get_socket(self):
        return self.socket

    def is_connected(self):
        return self.connected


def handle_client(client):
    while client.is_connected():
        try:
            # while True:
            #     msg = client.receive_message()
            #     if DEBUG_MODE: print(msg)
            client.send_message(input(f"{client.get_name()}: "))
          
        except IOError as e:
            if DEBUG_MODE and e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print("Reading error: {}".format(str(e)))
                sys.exit(1)
            continue

        except Exception as e:
            if DEBUG_MODE: print("Reading error: {}".format(str(e)))
            sys.exit(1)


def run():
    client = ChatClient(PORT, input("Username: "))
    client.connect(input("server: "), input("port: "))

    client_thread = threading.Thread(target=handle_client, args=(client,))
    client_thread.start()
