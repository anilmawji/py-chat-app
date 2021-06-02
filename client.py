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
HEIGHT = 500
THEME_COLOR = "#0D1216"

class ChatClient:
    def __init__(self, port, name='Unknown'):
        self.port = port
        self.name = name
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False

    def connect(self, server_address='127.0.0.1'):
        try:
            self.socket.connect((server_address, self.port))
            self.socket.setblocking(False)
            self.connected = True

            name_data = self.name.encode(ENCODING)
            name_header = f"{len(name_data):<{HEADER_LENGTH}}".encode(ENCODING)
            self.socket.sendall(name_header + name_data)

            if DEBUG_MODE:
                print(f"[CONNECTED] you are now connected to {server_address}:{self.port}")

        except socket.error as e:
            if DEBUG_MODE:
                print("Socket error: {}".format(str(e)))
            sys.exit(1)

    def send_message(self, msg):
        if msg:
            msg_data = msg.encode(ENCODING)
            msg_header = f"{len(msg_data):<{HEADER_LENGTH}}".encode(ENCODING)
            self.socket.sendall(msg_header + msg_data)

    def receive_message(self):
        name_header = self.socket.recv(HEADER_LENGTH)

        if not len(name_header):
            if DEBUG_MODE:
                print("[DISCONNECTED] connection closed by server")
            sys.exit(0)

        name_length = int(name_header.decode(ENCODING).strip())
        name = self.socket.recv(name_length).decode(ENCODING)

        msg_header = self.socket.recv(HEADER_LENGTH)
        msg_length = int(msg_header.decode(ENCODING).strip())
        msg = self.socket.recv(msg_length).decode(ENCODING)

        return self.format_message(name, msg)

    def format_message(self, name, msg):
        return name + ": " + msg

    def close(self):
        self.connected = False
        self.socket.close()

        if DEBUG_MODE:
            print(f"[DISCONNECTED] ended connection with server")

    def get_name(self):
        return self.name

    def get_socket(self):
        return self.socket

    def is_connected(self):
        return self.connected


class GUI:
    def __init__(self, client):
        self.client = client
        self.root = tk.Tk()
        self.root.title("Chatroom")
        self.root.configure(width=WIDTH, height=HEIGHT, bg=THEME_COLOR)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.minsize(WIDTH, HEIGHT)

        name_label = tk.Label(
            self.root,
            bg=THEME_COLOR,
            fg='white',
            text=self.client.name,
            font='Helvetica 13 bold',
            pady=5)
        name_label.place(relwidth=1)

        border_line = tk.Label(self.root, width=WIDTH, bg='white')
        border_line.place(relwidth=1, rely=0.07, relheight=0.012)

        self.chat_msgs = tk.Text(
            self.root,
            bg=THEME_COLOR,
            fg='white',
            font='Helvetica 10',
            padx=5,
            pady=5,
            wrap=tk.WORD,
            cursor='arrow',
            state=tk.DISABLED)
        self.chat_msgs.place(
            relwidth = 1,
            relheight = 0.92,
            rely = 0.08)

        bottom_frame = tk.Label(self.root, bg=THEME_COLOR, height=80)
        bottom_frame.place(rely=0.92, relwidth=1, relheight=0.08)

        self.msg_box = tk.Entry(bottom_frame, bg='white')
        self.msg_box.place(
            relx=0,
            rely=0.1,
            relwidth=0.8,
            relheight=0.8)
        self.msg_box.focus()

        self.send_button = tk.Button(
            bottom_frame,
            text='Send',
            bg=THEME_COLOR,
            fg='white',
            command=self.send_message)
        self.send_button.place(
            relx=1,
            rely=0.1,
            relwidth=0.2,
            relheight=0.8,
            anchor='ne')

        scrollbar = tk.Scrollbar(self.chat_msgs)
        scrollbar.place(relheight=1, relx=0.974)
        scrollbar.config(command=self.chat_msgs.yview)

    def send_message(self):
        msg = self.msg_box.get().strip()
        self.msg_box.delete(0, tk.END)

        if len(msg):
            self.display_message(self.client.format_message('You', msg))
            self.client.send_message(msg)

    def display_message(self, msg):
        self.chat_msgs.config(state=tk.NORMAL)
        self.chat_msgs.insert(tk.END, msg + "\n\n")
        self.chat_msgs.config(state=tk.DISABLED)
        self.chat_msgs.see(tk.END)

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
                msg = client.receive_message()
                gui.display_message(msg)

                if DEBUG_MODE:
                    print(msg)

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
