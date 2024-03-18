import socket
import time
import peer_state


TEXT_ENCODING = 'utf-8'


class Node():
    def __init__(self, address: str = "127.0.0.1", port: int = 35654, debug_mode: bool = True):
        self.address = address
        self.port = port
        self.debug_mode = debug_mode
        self.header_length = 1024
        self.text_encoding = TEXT_ENCODING


    def start(self, *args, **kwargs):
        pass
    
    def connect_to_tracker(self, server_id: str, address: str, port: int, file_name: str, mode: str = "leach"):
        if [tracker for tracker in self._tracker_connections if tracker["id"] == server_id]:
            if self.debug_mode:
                print(f"[{self.get_peer_name(self._socket)}] error: already connected to {address}:{port}")
            return False

        try:
            self.tracker_socket.connect((address, port))
            self.tracker_socket.setblocking(False)
            self.tracker_socket.settimeout(3)

            # msg: connect: <filename>:<ip>:<port>
            self.send_message(self.tracker_socket, f"{mode}:{file_name}:{self.address}:{self.port}")

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
        address, port = peer_socket.getpeername()
        
        return address + ":" + str(port)


    def send_message(self, recv_socket: socket.socket, message: str):
        data = message.encode(TEXT_ENCODING)
        header = f"{len(data):<{self.header_length}}".encode(TEXT_ENCODING)
        recv_socket.sendall(header + data)


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
