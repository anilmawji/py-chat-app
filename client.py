import socket
import select
import sys

HEADER_LENGTH = 10
ENCODING = "UTF-8"

class ChatClient():
    def __init__(self, port=1234, username='Unknown', debug_mode=False):
        self.port = port
        self.username = username
        self.debug_mode = debug_mode
        self.connected = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setblocking(False)

    def connect(self, address='127.0.0.1'):
        try:
            self.socket.connect((address, self.port))
            self.connected = True

            if self.debug_mode:
                print(f"You are now connected to {address}:{self.port}")

            encoded_username = self.username.encode(ENCODING)
            username_header = f"{len(encoded_username):<{HEADER_LENGTH}}".encode(ENCODING)
            self.socket.send(username_header + encoded_username)

        except socket.error:
            if self.debug_mode:
                print(f"Could not connect to {address}:{self.port}")
            sys.exit(1)

        while self.connected:
            message = self.format_message(input())
            self.send_message(message)

            try:
                while True:
                    print(self.receive_message())

            except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    if self.debug_mode:
                        print('Reading error: {}'.format(str(e)))
                    sys.exit()
                continue

            except Exception as e:
                if self.debug_mode:
                    print('Reading error: '.format(str(e)))
                sys.exit()

    def format_message(self, message, username=self.username):
        return username + " > " + message

    def send_message(self, message):
        if message:
            message = self.format_message(message).encode(ENCODING)
            message_header = f"{len(message):<{HEADER_LENGTH}}".encode(ENCODING)
            client_socket.sendall(message_header + message)

    def receive_message(self):
        username_header = client_socket.recv(HEADER_LENGTH)

        if not len(username_header):
            if self.debug_mode:
                print('Connection closed by server')
            sys.exit()

        username_length = int(username_header.decode(ENCODING).strip())
        username = client_socket.recv(username_length).decode(ENCODING)

        message_header = client_socket.recv(HEADER_LENGTH)
        message_length = int(message_header.decode(ENCODING).strip())
        message = client_socket.recv(message_length).decode(ENCODING)

        return self.format_message(message, username)

    def get_username(self):
        return self.username

    def is_connected(self):
        return self.connected


def main():
    username = input("Username: ")
    client = ChatClient(username=username, debug_mode=True)
    client.connect()

if __name__ == "__main__":
    main()
