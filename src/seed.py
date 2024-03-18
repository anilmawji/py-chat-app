from node import Node

import socket
import select
import peer_state


class Seed(Node):
    def __init__(self, address: str = "127.0.0.1", port: int = 6000, debug_mode: bool = False):
        super().__init__(address, port, debug_mode)
        self._state = peer_state.INITIAL
        self._tracker_connections = [] # List of connected tracker tuples - (ip_address, port, socket)
        self._peer_sockets = [] # List of connected peer sockets
        self._pieces = [] # List of piece / peer tuples - (piece, peer)
        
        self.tracker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.header_length = 1024


    def start(self, *args, **kwargs):
        tracker_address = kwargs.get("tracker_address") or "127.0.0.1"
        tracker_port = int(kwargs.get("tracker_port") or 6969)

        self.connect_to_tracker("tracker", tracker_address, tracker_port, "alice.torrent", "seed")

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setblocking(False)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind((self.address, self.port))
        self._socket.listen(50) # max 50 peer connections

        if self.debug_mode:
            print(f"Started listening for connections on {self.address}:{self.port}...")
        
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
                        print(f"Accepted connection from peer: {self.get_peer_name(peer_socket)}")

                        self._peer_sockets.append(peer_socket)
                    else:
                        # Otherwise assume the message was from a peer
                        message = self.receive_peer_request(sock)
                        
                        if message:
                            #print(f"message from peer {message}")
                            self.handle_peer_request(sock, message)

                for sock in exceptional:
                    self.disconnect(sock)
        except (SystemExit, KeyboardInterrupt):
            return
