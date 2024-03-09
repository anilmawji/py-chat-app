from server import Server


def on_message_received(msg_header, msg_data):
    #print("ok: ", msg_data)
    pass

s = Server("SERVER", "127.0.0.1", 12345, 10, on_message_received, debug_mode=True)
s.start()
