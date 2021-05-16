import socket
import select

HEADER_LENGTH = 10
ENCODING = "UTF-8"

class ChatServer():
	def __init__(self, address='', port=1234):
		self.address = address
		self.port = port
		self.clients = {}
		self.running = False
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.setblocking(False)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
		self.socket.bind((self.address, self.port))

	def start(self, max_clients=100):
		print(f"[STARTED] Listening for connections on {self.address}:{self.port}...")
		self.socket.listen(max_clients)
		self.running = True

	def accept_connection(self):
		client_socket, client_address = self.socket.accept()
		user = self.receive_msg(client_socket)

		if user:
			self.clients[client_socket] = user
			print("[CONNECTED] {} has joined the chat from {}:{}".format(user['data'].decode(ENCODING), *client_address))
			return client_socket, client_address
		return None, None

	def receive_msg(self, client_socket):
		try:
			msg_header = client_socket.recv(HEADER_LENGTH)
			if not len(msg_header): return False

			message_length = int(msg_header.decode(ENCODING).strip())
			data = client_socket.recv(message_length)

			if client_socket in self.clients:
				user = self.clients[client_socket]
				print(f"[RECEIVED] Got message from {user['data'].decode(ENCODING)}: {data.decode(ENCODING)}")

			return {'header': msg_header, 'data': data}
		except:
			return None

	def broadcast_msg(self, client_socket, message):
		user = self.clients[client_socket]
		if not user: return False

		for socket in self.clients:
			if socket != client_socket:
				socket.sendall(user['header'] + user['data'] + message['header'] + message['data'])
		return True

	def end_connection(self, client_socket):
		print("[DISCONNECTED] ended connection with: {}".format(self.clients[client_socket]['data'].decode(ENCODING)))
		del self.clients[client_socket]

	def stop(self):
		self.socket.close()
		self.running = False

	def get_clients(self):
		return self.clients

	def is_running(self):
		return self.running

	def get_socket(self):
		return self.socket


def main():
	server = ChatServer()
	server.start()
	socket_list = [server.get_socket()]

	while server.is_running():
		readable, _, exceptional = select.select(socket_list, [], socket_list)

		for sock in readable:
			if sock == server.get_socket():
				client_socket, client_address = server.accept_connection()
				if client_socket:
					socket_list.append(client_socket)
			else:
                msg = server.receive_msg(sock)
				if msg:
                    server.broadcast_msg(sock, msg)
				else:
					server.end_connection(sock)
					socket_list.remove(sock)

		for sock in exceptional:
			server.end_connection(sock)
			socket_list.remove(sock)

if __name__ == "__main__":
	main()
