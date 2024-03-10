import socket
import select
from peer import Peer


TEXT_ENCODING = 'utf-8'


# To start with, we will only support HTTP trackers and not UDP trackers
class Tracker():

    def __init__(
        self,
        address: str,
        port: int,
        debug_mode: bool = False,
    ):
        self.id = address + ":" + port
        self.debug_mode = debug_mode
        self._running = False
        self._peer_sockets = {}
        self._torrents = []


    def listen_for_peer_requests(self, max_clients: int = 100):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setblocking(False)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind((self.address, self.port))
        self._socket.listen(max_clients)

        if self.debug_mode:
            print(f"[{self.id}] started listening for connections on {self.address}:{self.port}...")
        
        self._running = True

        try:
            while self._running:
                socket_list = [self._socket] + self._peer_sockets
                # Get sockets ready to read from & sockets that threw an error
                # Use a timeout of 2 seconds so we periodically interrupt the select call to check for exceptions
                readable, _, exceptional = select.select(socket_list, [], socket_list, 2)

                for sock in readable:
                    # Check if we are ready to read in a new connection from the server socket
                    if sock == self._socket:
                        peer_socket, _ = self._socket.accept()

                        if message := self.receive_peer_request(peer_socket):
                            self._peer_sockets[peer_socket] = True  # TODO: Only register peer if the request is of valid form
                            self.handle_peer_request(peer_socket, message)
                        else:
                            # Peer did not send a request with the initial connection
                            self.disconnect(peer_socket)
                    else:
                        message = self.receive_peer_request(sock)
                        # Otherwise assume the message was from a peer
                        if message:
                            self.handle_peer_request(sock, message)

                for sock in exceptional:
                    self.disconnect(sock)
        except (SystemExit, KeyboardInterrupt):
            self.stop()


    # Temporary message handler, tracker accepts text only instead of GET requests
    def receive_peer_request(self, peer_socket: socket.socket):
        try:
            # TODO: Parse requests of arbirary size
            message = peer_socket.recv(10)

            if self.debug_mode and self._peer_sockets[peer_socket]:
                peer_name = self.get_peer_name(peer_socket)
                print(f"[{peer_name}] {message.decode(TEXT_ENCODING)}")

            return message
        except:
            return None


    def handle_peer_request(self, peer_socket: socket.socket, message: str):
        # TODO: Parse request type and call send_response_to_peer()
        pass


    def get_peer_name(self, peer_socket: socket.socket):
        address, port = peer_socket.getsockname()
        
        return address + ":" + port


    def disconnect(self, peer_socket: socket.socket):
        peer_is_connected = self._peer_sockets[peer_socket]
        peer_name = self.get_peer_name(peer_socket)

        if not peer_is_connected:
            if self.debug_mode:
                print(f"[{self.id}] Error: a connection with \"{peer_name}\" does not exist")
            return False

        del self._peer_sockets[peer_socket]

        if self.debug_mode:
            print(f"[{self.id}] connection with \"{peer_name}\" has ended")


    def send_response_to_peer(swelf, peer_socket: socket.socket):
        pass


    def stop_listening():
        pass