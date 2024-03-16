import socket
import select
import peer_state
from torrent import Torrent

class Peer():
    def __init__(self):
        self._torrent = None
        self._state = peer_state.INITIAL
        self._tracker_connections = [] # List of connected tracker tuples - (ip_address, port, socket)
        self._peer_connections = [] # List of connected peer tuples - (ip_address, port)
        self._pieces = [] # List of piece / peer tuples - (piece, peer)
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.header_length = 1024

        self.encoding = "utf-8"
        self.debug_mode = True


    def get_torrent(self, file_path: str):
        self._torrent = Torrent.read_metadata(file_path)
        for tracker in self._torrent.tracker_endpoints:
            if self.connect_to_tracker(tracker[0], tracker[1], tracker[2]):
                break


    def connect_to_tracker(self, server_id: str, address: str, port: int):
        if [tracker for tracker in self._tracker_connections if tracker["id"] == server_id]:
            if self.debug_mode:
                print(f"[{self.id}] error: already connected to {address}:{port}")
            return False

        try:
            self.socket.connect((address, port))
            self.socket.setblocking(False)

            print(self.get_peer_name(self.socket))

            # msg: connect: <filename>
            name_data = f"{self.get_peer_name(self.socket)}".encode(self.encoding)
            name_header = f"{len(name_data):<{self.header_length}}".encode(self.encoding)
            self.socket.sendall(name_header + name_data)
            print(f"Sent name data: {name_data}")

            self._tracker_connections.append({
                "id": server_id,
                "address": address,
                "port": port,
                "socket": self.socket
            })

            msg_header = self.socket.recv(1024)

            if not len(msg_header): return None

            msg_length = int(msg_header.decode(self.encoding).strip())
            message = self.socket.recv(msg_length).decode(self.encoding)
            print(f"Received message: {message}")


            if self.debug_mode:
                print(f"Peer successfully connected to {address}:{port}")

            return True

        except socket.error as e:
            if self.debug_mode:
                print(f"Peer socket error: {str(e)}")
            return False


    def get_peer_name(self, peer_socket: socket.socket):
        address, port = peer_socket.getsockname()
        
        return address + ":" + str(port)

    
    def send_tracker_request(self):
        pass


    def start_seeding(self, torrent: Torrent):
        pass


    def stop_seeding(self, torrent: Torrent):
        pass

    
def main():
    peer = Peer()
    peer.get_torrent(input("Enter the path to the .torrent file: "))

if __name__ == "__main__":
    main()
