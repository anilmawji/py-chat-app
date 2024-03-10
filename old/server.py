import socket
import select
from typing import Callable, Optional


TEXT_ENCODING = 'utf-8'


class Server():
    def __init__(
        self,
        id: str,
        address: str,
        port: int,
        header_length: int,
        on_message_received: Optional[Callable] = None,
        debug_mode: bool = False,
    ):
        self.id = id
        self.address = address
        self.port = port
        self.header_length = header_length
        self._on_message_received = on_message_received
        self.debug_mode = debug_mode
        self._running = False
        self._clients = {}


    def start(self, max_clients: int = 100):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setblocking(False)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind((self.address, self.port))
        self._socket.listen(max_clients)

        if self.debug_mode:
            print(f"[{self.id}] started listening for connections on {self.address}:{self.port}...")
        
        self._running = True
        socket_list = [self._socket]

        try:
            while self._running:
                # Get sockets ready to read from & sockets that threw an error
                # Use a timeout of 2 seconds so we periodically interrupt the select call to check for exceptions
                readable, _, exceptional = select.select(socket_list, [], socket_list, 2)

                for sock in readable:
                    # Check if we are ready to read in a new connection from the server socket
                    if sock == self._socket:
                        client_socket, _ = self.accept_connection()

                        if client_socket:
                            socket_list.append(client_socket)
                    else:
                        # Otherwise assume the message was from a client
                        if not self.receive_message(sock):
                            # End the connection if the message was empty
                            socket_list.remove(sock)
                            self.disconnect(sock)

                for sock in exceptional:
                    socket_list.remove(sock)
                    self.disconnect(sock)
        except (SystemExit, KeyboardInterrupt):
            self.stop()


    def stop(self):
        if not self._running: return False

        self._running = False
        self._socket.close()
        self._clients = {}

        if self.debug_mode:
            print(f"[{self.id}] stopped listening for connections on {self.address}:{self.port}...")
        
        return True


    def accept_connection(self):
        client_socket, client_address = self._socket.accept()
        client_id: bytes = self.receive_message(client_socket)

        if client_id:
            self._clients[client_socket] = client_id

            if self.debug_mode:
                print(f"[{self.id}] \"{client_id.decode(TEXT_ENCODING)}\" has connected from {client_address[0]}:{client_address[1]}")

            return client_socket, client_address
        return None, None
    

    def disconnect(self, client_socket: socket.socket):
        user = self._clients[client_socket]

        if not user:
            if self.debug_mode:
                print(f"[{self.id}] Error: a connection with \"{user['data'].decode(self.encoding)}\" does not exist")
            return False

        del self._clients[client_socket]

        if self.debug_mode:
            print(f"[{self.id}] connection with \"{user['data'].decode(self.encoding)}\" has ended")


    def receive_message(self, client_socket: socket.socket):
        try:
            msg_header = client_socket.recv(self.header_length)

            if not len(msg_header): return None

            msg_length = int(msg_header.decode(self.encoding).strip())
            msg_data = client_socket.recv(msg_length)

            if self.debug_mode and client_socket in self._clients:
                user = self._clients[client_socket]
                print(f"[{user['data'].decode(self.encoding)}] {msg_data.decode(self.encoding)}")

            if msg_header and msg_data:
                self._on_message_received(msg_header, msg_data)
            
            #self.send_message(client_socket, "hello from the server side")

            return {'header': msg_header, 'data': msg_data}
        except:
            return None


    def send_message(self, client_socket: socket.socket, message: str):
        if not message: return

        message = self.encode_message(message)
        
        if client_socket in self._clients:
            client_socket.sendall(message)


    def broadcast_message(self, message: str):
        if not message: return

        message = self.encode_message(message)

        for socket in self._clients:
            socket.sendall(message)


    def encode_message(self, message: str):
        name_data = self.id.encode(self.encoding)
        name_header = f"{len(name_data):<{self.header_length}}".encode(self.encoding)

        msg_data = message.encode(self.encoding)
        msg_header = f"{len(msg_data):<{self.header_length}}".encode(self.encoding)

        return name_header + name_data + msg_header + msg_data


    def get_id(self):
        return self.id


    def get_address(self):
        return self.address
    

    def get_port(self):
        return self.port
    

    def get_encoding(self):
        return self.encoding


    def get_header_length(self):
        return self.header_length

    @property
    def is_running(self):
        return self._running
