import socket
import select


class Client:
    def __init__(
        self,
        id: str,
        header_length: int,
        encoding: str = "UTF-8",
        debug_mode: bool = False
    ):
        self.id = id
        self.header_length = header_length
        self.encoding = encoding
        self.debug_mode = debug_mode
        self._running = False
        self._connections = {}
    

    def start(self):
        self._running = True

        try:
            while self._running:
                socket_list = self._connections.values()
                readable, _, exceptional = select.select(socket_list, [], socket_list, 2)
            
                for sock in readable:
                    if self.receive_message(sock):
                        pass

                for sock in exceptional:
                    socket_list.remove(sock)
                    self.disconnect(sock)
        except (SystemExit, KeyboardInterrupt):
            self.stop()
    

    def stop(self):
        if not self._running: return False

        self._running = False
        self.disconnect_all()

        if self.debug_mode:
            print(f"[{self.id}] closed all connections")

        return True


    def connect(self, server_id: str, server_address: str, server_port: int):
        if self._connections.get(server_id):
            if self.debug_mode:
                print(f"[{self.id}] error: already connected to {server_address}:{server_port}")
            return False

        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((server_address, server_port))
            client_socket.setblocking(False)

            name_data = self.id.encode(self.encoding)
            name_header = f"{len(name_data):<{self.header_length}}".encode(self.encoding)
            client_socket.sendall(name_header + name_data)

            self._connections[server_id] = client_socket

            if self.debug_mode:
                print(f"[{self.id}] successfully connected to {server_address}:{server_port}")

            return True

        except socket.error as e:
            if self.debug_mode:
                print(f"[{self.id}] socket error: {str(e)}")
            return False


    def disconnect(self, server_id: str):
        client_socket: socket.socket = self._connections.get(server_id)

        if not client_socket:
            if self.debug_mode:
                print(f"[{self.id}] error: failed to disconnect from \"{server_id}\": not connected")
            return False

        try:
            client_socket.close()
            self._connections[server_id] = None

            if self.debug_mode:
                print(f"[{self.id}] disconnected from \"{server_id}\"")

            return True

        except socket.error as e:
            if self.debug_mode:
                print(f"[{self.id}] error: failed to disconnect from \"{server_id}\": {str(e)}")
            return False


    def disconnect_all(self):
        for server_id, client_socket in self._connections:
            try:
                client_socket.close()
                self._connections[server_id] = None
            except socket.error as e:
                if self.debug_mode:
                    print(f"[{self.id}] error: failed to disconnect from \"{server_id}\": {str(e)}")


    def send_message(self, server_id: str, message: str):
        client_socket: socket.socket = self._connections.get(server_id)

        if not client_socket:
            if self.debug_mode:
                print(f"[{self.id}] error: not connected to the \"{server_id}\"")
            return False

        if message:
            msg_data = message.encode(self.encoding)
            msg_header = f"{len(msg_data):<{self.header_length}}".encode(self.encoding)
            client_socket.sendall(msg_header + msg_data)


    def receive_message(self, server_id: str):
        client_socket: socket.socket = self._connections[server_id]
        name_header = client_socket.recv(self.header_length)

        if not len(name_header):
            if self.debug_mode:
                print(f"[{self.id}] forcefully disconnected from \"{server_id}\"")
            return None

        name_length = int(name_header.decode(self.encoding).strip())
        name = client_socket.recv(name_length).decode(self.encoding)

        msg_header = client_socket.recv(self.header_length)
        msg_length = int(msg_header.decode(self.encoding).strip())
        message = client_socket.recv(msg_length).decode(self.encoding)

        return name + ": " + message
    

