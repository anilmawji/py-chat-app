import socket
import select

ADDRESS = "127.0.0.1"
PORT = 1234
DEBUG_MODE = True
HEADER_LENGTH = 10
ENCODING = "UTF-8"

class ChatServer():
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.running = False
        self.clients = {}
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setblocking(False)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.address, self.port))

    def start(self, max_clients=100):
        self.running = True
        self.socket.listen(max_clients)

        if DEBUG_MODE:
            print(f"[STARTED] listening for connections over {self.address}:{self.port}...")

    def accept_connection(self):
        client_socket, client_address = self.socket.accept()
        user = self.receive_message(client_socket)

        if user:
            self.clients[client_socket] = user
            self.send_announcement(f"{user['data'].decode(ENCODING)} has joined the chat!")

            if DEBUG_MODE:
                print("[CONNECTED] \"{}\" has joined the chat over {}:{}".format(user['data'].decode(ENCODING), *client_address))

            return client_socket, client_address
        return None, None

    def send_announcement(self, msg):
        if msg:
            name_data = "SERVER".encode(ENCODING)
            name_header = f"{len(name_data):<{HEADER_LENGTH}}".encode(ENCODING)

            msg_data = msg.encode(ENCODING)
            msg_header = f"{len(msg_data):<{HEADER_LENGTH}}".encode(ENCODING)

            for socket in self.clients:
                socket.sendall(name_header + name_data + msg_header + msg_data)

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

    def broadcast_message(self, client_socket, msg):
        user = self.clients[client_socket]
        if not user: return False

        for socket in self.clients:
            if socket != client_socket:
                socket.sendall(user['header'] + user['data'] + msg['header'] + msg['data'])
        return True

    def end_connection(self, client_socket):
        user = self.clients[client_socket]
        if not user: return False

        self.send_announcement(f"{user['data'].decode(ENCODING)} has left the chat")

        if DEBUG_MODE:
            print("[DISCONNECTED] connection with \"{}\" has ended".format(user['data'].decode(ENCODING)))

        del self.clients[client_socket]

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
    server = ChatServer(ADDRESS, PORT)
    server.start()
    socket_list = [server.get_socket()]

    try:
        while server.is_running():
            readable, _, exceptional = select.select(socket_list, [], socket_list)

            for sock in readable:
                if sock == server.get_socket():
                    client_socket, _ = server.accept_connection()
                    if client_socket:
                        socket_list.append(client_socket)
                else:
                    msg = server.receive_message(sock)
                    if msg:
                        server.broadcast_message(sock, msg)
                    else:
                        socket_list.remove(sock)
                        server.end_connection(sock)

            for sock in exceptional:
                socket_list.remove(sock)
                server.end_connection(sock)

    except (SystemExit, KeyboardInterrupt):
        server.stop()

if __name__ == "__main__":
    main()
