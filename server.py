import socket
import select

HEADER_LENGTH = 10
ENCODING = "UTF-8"

class ChatServer():
    def __init__(self, address='', port=1234, debug_mode=False):
        self.address = address
        self.port = port
        self.debug_mode = debug_mode
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

        if self.debug_mode:
            print(f"[STARTED] Listening for connections over {self.address}:{self.port}...")

        while self.running:
            readable, _, exceptional = select.select(self.socket_list, [], self.socket_list)

            for sock in readable:
                if sock == self.socket:
                    client_socket = None
                    try:
                        client_socket, client_address = self.accept_connection()
                        if client_socket:
                            self.socket_list.append(client_socket)
                    except KeyboardInterrupt:
                        if client_socket:
                            client_socket.close()
                        break
                else:
                    msg = self.receive_message(sock)
                    if msg:
                        self.broadcast_message(sock, msg)
                    else:
                        self.end_connection(sock)
                        self.socket_list.remove(sock)

            #Sanity check for potentially faulty connections
            for sock in exceptional:
                self.end_connection(sock)
                self.socket_list.remove(sock)

    def accept_connection(self):
        client_socket, client_address = self.socket.accept()
        user = self.receive_message(client_socket)

        if user:
            self.clients[client_socket] = user

            if self.debug_mode:
                print("[CONNECTED] {} has joined the chat from {}:{}".format(user['data'].decode(ENCODING), *client_address))

            return client_socket, client_address
        return None, None

    def receive_message(self, client_socket):
        try:
            msg_header = client_socket.recv(HEADER_LENGTH)
            if not len(msg_header): return False

            msg_length = int(msg_header.decode(ENCODING).strip())
            data = client_socket.recv(msg_length)

            if self.debug_mode and client_socket in self.clients:
                user = self.clients[client_socket]
                print(f"[RECEIVED] {user['data'].decode(ENCODING)} says: {data.decode(ENCODING)}")

            return {'header': msg_header, 'data': data}
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
        if self.debug_mode:
            print("[DISCONNECTED] ended connection with: {}".format(self.clients[client_socket]['data'].decode(ENCODING)))

        del self.clients[client_socket]

    def stop(self):
        self.running = False
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()

        if self.debug_mode:
            print(f"[STOPPED] The server has closed all connections over {self.address}:{self.port}...")

    def is_running(self):
        return self.running

    def get_clients(self):
        return self.clients

    def get_socket(self):
        return self.socket


def main():
    server = ChatServer(debug_mode=True)
    try:
        server.start()
    except (SystemExit, KeyboardInterrupt):
        server.stop()

if __name__ == "__main__":
    main()
