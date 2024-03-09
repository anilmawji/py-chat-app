import old.client_old as client_old
import old.server_old as server_old
import threading

def main():
    port = input("port: ")
    threading.Thread(target=server_old.run, args=(port,)).start()
    client_old.run()

if __name__ == "__main__":
    main()
