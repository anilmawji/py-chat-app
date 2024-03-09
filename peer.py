from old.client_old import ChatClient
import threading


print("starting client")
c = ChatClient(23456, "karl")
c.connect("127.0.0.1", 12345)
c = threading.Thread(target=c.run)
c.start()
