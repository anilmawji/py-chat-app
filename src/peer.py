import peer_state
from torrent import Torrent
import socket

class Peer():
    def __init__(self):
        self._torrent = None
        self._state = peer_state.INITIAL
        self._tracker_connections = [] # List of connected tracker tuples - (ip_address, port)
        self.peer_connections = [] # List of connected peer tuples - (ip_address, port)
        self.pieces = [] # List of piece / peer tuples - (piece, peer)
        self._connections = {}


    def connect_with_trackers(self, torrent: Torrent):
        self._trackers = torrent.tracker_endpoints

        for tracker in Torrent.tracker_endpoints:
            connection = self.connect(tracker.id, tracker.tracker_address, int(tracker.tracker_port))
            if connection:
                self._tracker_connections.append(connection)
                print(f"Connected to tracker {tracker.tracker_address}:{tracker.tracker_port}")
                return
            

    
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