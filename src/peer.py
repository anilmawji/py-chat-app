import socket
import select
import peer_state
import time
from torrent import Torrent


TEXT_ENCODING = 'utf-8'


class Peer():
    def __init__(self, address: str = "127.0.0.1", port: int = 35654, debug_mode: bool = True):
        self._state = peer_state.INITIAL
        self.address = address
        self.port = port
        self._tracker_connections = [] # List of connected tracker tuples - (ip_address, port, socket)
        self._peer_sockets = [] # List of connected peer sockets
        self._pieces = [] # List of piece / peer tuples - (piece, peer)
        
        self.tracker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.header_length = 1024

        self.debug_mode = True


    def get_torrent(self, file_name: str):
        self._torrent = Torrent.read_metadata(file_name)
        #self._torrent.tracker_endpoints.append(('http://localhost:6000', 'localhost', 6000))

        for tracker in self._torrent.tracker_endpoints:
            print(f"Attempting to connect to tracker: {tracker}")

            msg = self.connect_to_tracker(tracker[0], tracker[1], tracker[2], file_name)
            if msg and msg != "failed":
                peer_names = msg.split(' ')

                for name in peer_names:
                    address, port = name.split(":")
                    port = int(port)
                    tracker_addr, tracker_port = self.tracker_socket.getsockname()

                    if tracker_port != port:
                        print(f"Peer info from tracker: {address} {port}")
                        self.connect_to_peer(address, port, file_name)
                break
            elif msg == "failed":
                continue

            while True:
                try:
                    if msg_header := self.tracker_socket.recv(1024):
                        msg_length = int(msg_header.decode(TEXT_ENCODING).strip())
                        msg = self.tracker_socket.recv(msg_length).decode(TEXT_ENCODING)

                        return msg

                except IOError as e:
                    time.sleep(1)


    def connect_to_tracker(self, server_id: str, address: str, port: int, file_name: str, mode: str = "leach"):
        if [tracker for tracker in self._tracker_connections if tracker["id"] == server_id]:
            if self.debug_mode:
                print(f"[{self.get_peer_name(self._socket)}] error: already connected to {address}:{port}")
            return False

        try:
            self.tracker_socket.connect((address, port))
            self.tracker_socket.setblocking(False)
            self.tracker_socket.settimeout(3)

            # msg: connect: <filename>
            name_data = f"{mode}:{file_name}:{self.address}:{self.port}".encode(TEXT_ENCODING)
            name_header = f"{len(name_data):<{self.header_length}}".encode(TEXT_ENCODING)
            self.tracker_socket.sendall(name_header + name_data)

            self._tracker_connections.append({
                "id": server_id,
                "address": address,
                "port": port,
                "socket": self.tracker_socket
            })

            if self.debug_mode:
                print(f"Connected to tracker {address}:{port}")
            
            while True:
                try:
                    if msg_header := self.tracker_socket.recv(1024):
                        msg_length = int(msg_header.decode(TEXT_ENCODING).strip())
                        msg = self.tracker_socket.recv(msg_length).decode(TEXT_ENCODING)
                        
                        print(f"Received response from tracker: {msg}")

                        return msg
                    
                except socket.timeout as e:
                    return "failed"
                except IOError as e:
                    time.sleep(1)

        except socket.error as e:
            if self.debug_mode:
                print(f"Peer socket error: {str(e)}")
            return "failed"


    def get_peer_name(self, peer_socket: socket.socket):
        address, port = peer_socket.getsockname()
        
        return address + ":" + str(port)


    def start_seeding(self, address, port, file_name):
        self.address = address
        self.port = port

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


    def receive_peer_request(self, peer_socket: socket.socket):
        try:
            msg_header = peer_socket.recv(1024)

            msg_length = int(msg_header.decode(TEXT_ENCODING).strip())
            message = peer_socket.recv(msg_length).decode(TEXT_ENCODING)
            
            print(f"Request for file from peer: {message}")

            return message
        except:
            return None
    

    def handle_peer_request(self, peer_socket: socket.socket, message: str):
        #print(f"message from peer: {message}")
        pass


    def disconnect(self, peer_socket: socket.socket):
        peer_name = self.get_peer_name(peer_socket)

        if not peer_socket in self._peer_sockets:
            if self.debug_mode:
                print(f"[{peer_name}] Error: a connection with \"{peer_name}\" does not exist")
            return False

        self._peer_sockets.remove(peer_socket)

        if self.debug_mode:
            print(f"[{peer_name}] connection with \"{peer_name}\" has ended")

    
    def connect_to_peer(self, address, port, file_name):
        try:
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.connect((address, port))
            peer_socket.setblocking(False)

            self._peer_sockets.append(peer_socket)

            print(f"Sending handshake to peer")

            name_data = file_name.encode(TEXT_ENCODING)
            name_header = f"{len(name_data):<{self.header_length}}".encode(TEXT_ENCODING)
            peer_socket.sendall(name_header + name_data)

            while True:
                self.receive_peer_request(peer_socket)
                # TODO: Check for new piece from peer
                time.sleep(1)


        except socket.error as e:
            if self.debug_mode:
                print(f"Peer socket error: {str(e)}")
            return None

    
def main():
    file_name = "alice.torrent"
    #file_name = input("Enter the path to the .torrent file: ")

    seeding = input("Enter 0 if downloading or 1 if seeding: ")

    peer = Peer()

    if seeding == "1":
        peer.connect_to_tracker("id", "127.0.0.1", 6969, file_name, "seed")
        peer.start_seeding("127.0.0.1", 35654, file_name)

    elif seeding == "0":
        peer.get_torrent(file_name)

if __name__ == "__main__":
    main()
