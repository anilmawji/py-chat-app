from node import Node
from torrent import Torrent
import socket
import time
import peer_state

TEXT_ENCODING = 'utf-8'

class Leach(Node):
    def __init__(self, address: str = "", port: int = 35654, debug_mode: bool = True):
        super().__init__(address, port, debug_mode)
        self._torrent = None
        self._state = peer_state.INITIAL
        self._tracker_connections = [] # List of connected tracker tuples - (ip_address, port, socket)
        self._peer_sockets = [] # List of connected peer sockets
        self._pieces = [] # List of piece / peer tuples - (piece, peer)
        
        self.tracker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.header_length = 1024

    def start(self, *args, **kwargs):
        file_name = kwargs.get("file_name")

        self._torrent = Torrent.read_metadata(file_name)
        #self._torrent.tracker_endpoints.append(('http://localhost:6000', 'localhost', 6000))

        for tracker in self._torrent.tracker_endpoints:
            print(f"Attempting to connect to tracker: {tracker}")

            msg = self.connect_to_tracker(tracker[0], tracker[1], tracker[2], file_name)
            
            if msg and msg != "failed":
                # Successful connection to tracker
                peer_names = msg.split(" ")

                for name in peer_names:
                    address, port = name.split(":")
                    port = int(port)

                    tracker_addr, tracker_port = self.tracker_socket.getsockname()

                    if tracker_port != port:
                        print(f"Peer info from tracker: {address} {port}")
                        self.connect_to_peer(address, port, file_name)
                break
            elif msg == "failed":
                # Failed to connect to tracker, attempt connection with next tracker
                continue

            while True:
                try:
                    if msg_header := self.tracker_socket.recv(1024):
                        msg_length = int(msg_header.decode(TEXT_ENCODING).strip())
                        msg = self.tracker_socket.recv(msg_length).decode(TEXT_ENCODING)

                        return msg

                except IOError as e:
                    time.sleep(1)

    
    def connect_to_peer(self, address, port, file_name):
        try:
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.connect((address, port))
            peer_socket.setblocking(False)

            self._peer_sockets.append(peer_socket)

            print(f"Sending handshake to peer")

            self.send_message(peer_socket, file_name)

            while True:
                self.receive_peer_request(peer_socket)
                # TODO: Check for new piece from peer
                time.sleep(1)


        except socket.error as e:
            if self.debug_mode:
                print(f"Peer socket error: {str(e)}")
            return None
