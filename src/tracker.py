import socket
import select
import time


TEXT_ENCODING = 'utf-8'


# To start with, we will only support HTTP trackers and not UDP trackers
class Tracker():

    def __init__(
        self,
        address: str,
        port: int,
        debug_mode: bool = False,
    ):
        self.id = address + ":" + str(port)
        self.address = address
        self.port = port
        self.debug_mode = debug_mode
        self._running = False
        self._peer_sockets = []
        self._seeds = {} # { <filename>: [peer1, peer2, ...] }
        self._leaches = {} # { <filename>: [peer1, peer2, ...] }


    def listen_for_peer_requests(self, max_clients: int = 100):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setblocking(False)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind((self.address, self.port))
        self._socket.listen(max_clients)

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
                        print(f"Accepted connection from: {self.get_peer_name(peer_socket)}")

                        self._peer_sockets.append(peer_socket)
                    else:
                        # Otherwise assume the message was from a peer
                        message = self.receive_peer_request(sock)
                        
                        if message:
                            #print(f"message from peer {message}")
                            self.handle_peer_request(sock, message)

                for sock in exceptional:
                    self.disconnect(sock)

                time.sleep(0.1)
        except (SystemExit, KeyboardInterrupt):
            self.stop()


    # Temporary message handler, tracker accepts text only instead of GET requests
    def receive_peer_request(self, peer_socket: socket.socket):
        try:
            msg_header = peer_socket.recv(1024)

            msg_length = int(msg_header.decode(TEXT_ENCODING).strip())
            message = peer_socket.recv(msg_length).decode(TEXT_ENCODING)

            return message
        except:
            return None


    def handle_peer_request(self, peer_socket: socket.socket, message: str):
        if message == "stop":
            self.disconnect(peer_socket)
            return
        elif message.startswith("leach:"):
            print(f"Handshake from peer: {message}")

            print(f"peer: {peer_socket.getpeername()}")
            file_name = message.split(":")[1].strip()
            if file_name not in self._leaches:
                self._leaches[file_name] = []

            self._leaches[file_name].append(peer_socket)
            print(f"seeds: {self._seeds}")
            self.send_peers_to_peer(peer_socket, file_name)
        elif message.startswith("seed:"):
            print(f"Handshake from peer: {message}")

            print(f"peer: {peer_socket.getpeername()}")
            _, file_name, req_addr, req_port = message.split(":")
            if file_name not in self._seeds:
                self._seeds[file_name] = []

            self._seeds[file_name].append([req_addr, req_port])
            print(f"seeds: {self._seeds}")
            self.send_ack(peer_socket)

    def stop(self):
        if not self._running: return False

        self._running = False
        self._socket.close()
        self._peer_sockets = []

        if self.debug_mode:
            print(f"Stopped listening for connections on {self.address}:{self.port}...")
        
        return True


    def get_peer_name(self, peer_socket: socket.socket):
        address, port = peer_socket.getpeername()
        
        return address + ":" + str(port)


    def disconnect(self, peer_socket: socket.socket):
        peer_name = self.get_peer_name(peer_socket)

        if not peer_socket in self._peer_sockets:
            if self.debug_mode:
                print(f"Error: a connection with \"{peer_name}\" does not exist")
            return False

        self._peer_sockets.remove(peer_socket)

        if self.debug_mode:
            print(f"Connection with \"{peer_name}\" has ended")


    def send_peers_to_peer(self, peer_socket: socket.socket, file_name: str):
        peer_list = self._seeds.get(file_name, []) # filename: [[addr, port], ...]
        peer_data = " ".join([f"{addr}:{port}" for addr, port in peer_list]).encode(TEXT_ENCODING)

        # msg: peers: <peer1> <peer2> ...
        peer_header = f"{len(peer_data):<{1024}}".encode(TEXT_ENCODING)
        peer_socket.sendall(peer_header + peer_data)

    def send_ack(self, peer_socket: socket.socket):
        ack_data = "ack".encode(TEXT_ENCODING)
        ack_header = f"{len(ack_data):<{1024}}".encode(TEXT_ENCODING)
        peer_socket.sendall(ack_header + ack_data)

    def stop_listening():
        pass
    
def main(address='localhost', port=6969):
    tracker = Tracker(address, port, debug_mode=True)
    tracker.listen_for_peer_requests()
    
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        main(sys.argv[1], int(sys.argv[2]))
    else:
        main()