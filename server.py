import socket
import select

DEBUG_MODE = True
HEADER_LENGTH = 10
ENCODING = "UTF-8"

class ChatServer():
    def __init__(self, address='127.0.0.1', port=1234):
        self.address = address
        self.port = port
        self.running = False
        self.clients = {}
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setblocking(False)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.address, self.port))
        self.socket_list = [self.socket]

    def start(self, max_clients=100):
        self.running = True
        self.socket.listen(max_clients)

        if DEBUG_MODE:
            print(f"[STARTED] listening for connections over {self.address}:{self.port}...")

        while self.running:
            readable, _, exceptional = select.select(self.socket_list, [], self.socket_list)

            for socket in readable:
                if socket == self.socket:
                    self.accept_connection()
                else:
                    msg = self.receive_message(socket)
                    if msg:
                        self.broadcast_message(socket, msg)
                    else:
                        self.end_connection(socket)

            for socket in exceptional:
                self.end_connection(socket)

    def accept_connection(self):
        client_socket, client_address = self.socket.accept()
        user = self.receive_message(client_socket)

        if user:
            self.socket_list.append(client_socket)
            self.clients[client_socket] = user

            if DEBUG_MODE:
                print("[CONNECTED] \"{}\" has joined the chat from {}:{}".format(user['data'].decode(ENCODING), *client_address))

            return client_socket, client_address
        return None, None

    def receive_message(self, client_socket):
        try:
            msg_header = client_socket.recv(HEADER_LENGTH)
            if not len(msg_header): return None

            msg_length = int(msg_header.decode(ENCODING).strip())
            msg_data = client_socket.recv(msg_length)

            if DEBUG_MODE and client_socket in self.clients:
                user = self.clients[client_socket]
                print(f"[RECEIVED] new message from \"{user['data'].decode(ENCODING)}\": {msg_data.decode(ENCODING)}")

            return {'header': msg_header, 'data': msg_data}
        except:
            return None

    def broadcast_message(self, client_socket, message):
        user = self.clients[client_socket]
        if not user: return False

        for socket in self.clients:
            if socket != client_socket:
                socket.sendall(user['header'] + user['data'] + message['header'] + message['data'])
        return True

    def end_connection(self, client_socket):
        user = self.clients[client_socket]
        if not user: return False

        if DEBUG_MODE:
            print("[DISCONNECTED] connection with \"{}\" has ended".format(user['data'].decode(ENCODING)))

        del self.clients[client_socket]
        self.socket_list.remove(client_socket)

    def stop(self):
        self.running = False
        self.socket.close()

        if DEBUG_MODE:
            print(f"[STOPPED] closed all connections over {self.address}:{self.port}...")

    def is_running(self):
        return self.running

    def get_clients(self):
        return self.clients

    def get_socket(self):
        return self.socket


def main():
    server = ChatServer()
    try:
        server.start()
    except SystemExit:
        server.stop()

if __name__ == "__main__":
    main()
