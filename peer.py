import peer_state


class Peer():
    def __init__(self):
        self._state = peer_state.INITIAL
        self._tracker_connections = []

    
    def send_tracker_request(self):
        pass
