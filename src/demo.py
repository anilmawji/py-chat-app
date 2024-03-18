from leach import Leach
from seed import Seed
from tracker import Tracker
# from node import Peer


def default_ports(mode):
    return {
        "tracker": 6969,
        "leach": 1235,
        "seed": 1236
    }.get(mode, 1234)


def main():
    mode = input("tracker, leach, or seed: ")

    address = input("Enter the address to bind to[127.0.0.1]: ") or "127.0.0.1"
    port = int(input(f"Enter the port to bind to[{default_ports(mode)}]: ") or default_ports(mode))

    if mode == "tracker":
        tracker = Tracker(address = address, port = port, debug_mode = True)
        tracker.start()

    elif mode == "leach":
        file_name = "alice.torrent"
        # file_name = input("Enter the path to the .torrent file: ")

        leach = Leach(address = address, port = port, debug_mode = True)
        leach.start(file_name=file_name)

    elif mode == "seed":
        default_tracker_port = default_ports("tracker")
        tracker_address = input("Enter the tracker address[127.0.0.1]: ") or "127.0.0.1"
        tracker_port = int(input(f"Enter the tracker port[{default_tracker_port}]: ") or default_tracker_port)

        seed = Seed(address = address, port = port, debug_mode = True)
        seed.start(tracker_address = tracker_address, tracker_port = tracker_port)



if __name__ == "__main__":
    main()

# def main(address='localhost', port=6969):
#     tracker = Tracker(address, port, debug_mode=True)
#     tracker.listen_for_peer_requests()
    
# if __name__ == "__main__":
#     import sys
#     if len(sys.argv) > 1:
#         main(sys.argv[1], int(sys.argv[2]))
#     else:
#         main()