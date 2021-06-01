import socket
import errno
import sys
import tkinter as tk
import threading

PORT = 1234
DEBUG_MODE = True
HEADER_LENGTH = 10
ENCODING = "UTF-8"

WIDTH = 325
HEIGHT = 450
THEME_COLOR = 'black'

class ChatClient:
    def __init__(self, port, username='Unknown'):
        self.port = port
        self.username = username
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False

    def connect(self, server_address='127.0.0.1'):
        try:
            self.socket.connect((server_address, self.port))
            self.socket.setblocking(False)
            self.connected = True

            encoded_username = self.username.encode(ENCODING)
            username_header = f"{len(encoded_username):<{HEADER_LENGTH}}".encode(ENCODING)
            self.socket.sendall(username_header + encoded_username)

            if DEBUG_MODE:
                print(f"[CONNECTED] you are now connected to {server_address}:{self.port}")

        except socket.error as e:
            if DEBUG_MODE:
                print("Socket error: {}".format(str(e)))
            sys.exit(1)

    def send_message(self, message):
        if message:
            encoded_message = message.encode(ENCODING)
            message_header = f"{len(encoded_message):<{HEADER_LENGTH}}".encode(ENCODING)
            self.socket.sendall(message_header + encoded_message)

    def receive_message(self):
        username_header = self.socket.recv(HEADER_LENGTH)

        if not len(username_header):
            if DEBUG_MODE:
                print("[DISCONNECTED] connection closed by server")
            sys.exit(0)

        username_length = int(username_header.decode(ENCODING).strip())
        username = self.socket.recv(username_length).decode(ENCODING)

        message_header = self.socket.recv(HEADER_LENGTH)
        message_length = int(message_header.decode(ENCODING).strip())
        message = self.socket.recv(message_length).decode(ENCODING)

        return self.format_message(username, message)

    def format_message(self, username, message):
        return username + " > " + message

    def close(self):
        self.connected = False
        self.socket.close()

        if DEBUG_MODE:
            print(f"[DISCONNECTED] ended connection with server")

    def get_username(self):
        return self.username

    def get_socket(self):
        return self.socket

    def is_connected(self):
        return self.connected


class GUI:
    def __init__(self, client):
        self.client = client
        self.root = tk.Tk()
        self.root.title("PyChat")
        self.root.configure(width=WIDTH, height=HEIGHT, bg=THEME_COLOR)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.minsize(WIDTH, HEIGHT)

        username_label = tk.Label(
            self.root,
            bg=THEME_COLOR,
            fg='white',
            text=self.client.username,
            font='Helvetica 13 bold',
            pady=5)
        username_label.place(relwidth=1)

        border_line = tk.Label(self.root, width=WIDTH, bg='white')
        border_line.place(relwidth=1, rely=0.07, relheight=0.012)

        self.chat_messages = tk.Label(
            self.root,
            width = 20,
            height = 2,
            bg=THEME_COLOR,
            fg='white',
            font='Helvetica 12',
            text='',
            padx=5,
            pady=5)
        self.chat_messages.place(
            relwidth = 1,
            relheight = 0.92,
            rely = 0.08)

        bottom_frame = tk.Label(self.root, bg=THEME_COLOR, height=80)
        bottom_frame.place(rely=0.92, relwidth=1, relheight=0.08)

        self.message_entry = tk.Entry(bottom_frame, bg='white')
        self.message_entry.place(
            relx=0,
            rely=0.1,
            relwidth=0.8,
            relheight=0.8)
        self.message_entry.focus()

        self.send_button = tk.Button(
            bottom_frame,
            text='Send',
            bg='black',
            fg='white',
            command=self.send_message)
        self.send_button.place(
            relx=1,
            rely=0.1,
            relwidth=0.2,
            relheight=0.8,
            anchor='ne')

    def send_message(self):
        message = self.message_entry.get().strip()
        self.message_entry.delete(0, tk.END)

        if len(message):
            self.display_message(self.client.format_message(self.client.username, message))
            self.client.send_message(message)

    def display_message(self, message):
        text = self.chat_messages.cget('text') + message + "\n"
        self.chat_messages.config(text=text)

    def get_client(self):
        return self.client

    def close(self):
        self.client.close()
        sys.exit(0)


def handle_client(gui):
    client = gui.get_client()

    while client.is_connected():
        try:
            while True:
                message = client.receive_message()
                gui.display_message(message)

                if DEBUG_MODE:
                    print(message)

        except IOError as e:
            if DEBUG_MODE and e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print("Reading error: {}".format(str(e)))
                sys.exit(1)
            continue

        except Exception as e:
            if DEBUG_MODE:
                print("Reading error: {}".format(str(e)))
            sys.exit(1)

def main():
    client = ChatClient(PORT, input("Username: "))
    client.connect()

    gui = GUI(client)

    client_thread = threading.Thread(target=handle_client, args=(gui,))
    client_thread.start()

    gui.root.mainloop()

if __name__ == "__main__":
    main()
