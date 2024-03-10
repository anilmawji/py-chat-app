class _PeerState():
    def __init__(self, am_choking, am_interested, peer_choking, peer_interested):
        self._am_choking = am_choking
        self._am_interested = am_interested
        self._peer_choking = peer_choking
        self._peer_interested = peer_interested


    def __eq__(self, peer): 
        if self._am_choking != peer.am_choking:
            return False
        if self.am_interested != peer.am_interested:
            return False
        if self.peer_choking != peer.peer_choking: 
            return False
        if self.peer_interested != peer.peer_interested:
            return False
        return True


    def  __ne__(self, peer):
        return not self.__eq__(peer)
    

# TODO: Create constants for all state types

INITIAL = _PeerState(
    am_choking=False,
    am_interested=False,
    peer_choking=False,
    peer_interested=False
)

D1 = _PeerState(
    am_choking=True,
    am_interested=True,
    peer_choking=True,
    peer_interested=False
)
