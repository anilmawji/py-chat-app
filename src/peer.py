import socket
import select
import peer_state
from torrent import Torrent

class Peer():
    def __init__(self):
        self._torrent = None
        self._state = peer_state.INITIAL
        self._tracker_connections = [] # List of connected tracker tuples - (ip_address, port)
        self._peer_connections = [] # List of connected peer tuples - (ip_address, port)
        self._pieces = [] # List of piece / peer tuples - (piece, peer)


    def connect_to_tracker(self, server_id: str, address: str, port: int):
        try:
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.connect((address, port))
            peer_socket.setblocking(False)

            name_data = f"{self.get_peer_name(peer_socket)}".encode(self.encoding)
            name_header = f"{len(name_data):<{self.header_length}}".encode(self.encoding)
            peer_socket.sendall(name_header + name_data)

            self._tracker_connections.append(peer_socket)

            if self.debug_mode:
                print(f"Peer successfully connected to {address}:{port}")

            return True

        except socket.error as e:
            if self.debug_mode:
                print(f"Peer socket error: {str(e)}")
            return False


    def get_peer_name(self, peer_socket: socket.socket):
        address, port = peer_socket.getsockname()
        
        return address + ":" + port

    
    def send_tracker_request(self):
        pass


    def start_seeding(self, torrent: Torrent):
        pass


    def stop_seeding(self, torrent: Torrent):
        pass
