import client
import server
import threading

def main():
    port = input("port: ")
    threading.Thread(target=server.run, args=(port,)).start()
    client.run()

if __name__ == "__main__":
    main()
