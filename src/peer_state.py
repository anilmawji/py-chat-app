class _PeerState():
    def __init__(self, am_choking, am_interested, peer_choking, peer_interested):
        self._am_choking = am_choking
        self._am_interested = am_interested
        self._peer_choking = peer_choking
        self._peer_interested = peer_interested

    #getter methods
    def am_choking(self):
        return self._am_choking
    
    def am_interested(self):
        return self._am_interested
    
    def peer_choking(self):
        return self._peer_choking
    
    def peer_interested(self):
        return self._peer_interested
    
    #setter methods
    def set_own_choking(self, choking: bool):
        self._am_choking = choking
    
    def set_own_interested(self, interested: bool):
        self._am_interested = interested

    def set_peer_choking(self, choking: bool):
        self._peer_choking = choking
    
    def set_peer_interested(self, choking: bool):
        self._peer_interested = choking

    def set_none(self):
        self._am_choking = None
        self._am_interested = None
        self._peer_choking = None
        self._peer_interested = None

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
    
    def __str__(self):
        stateLog = f'''(client choking: {str(self._am_choking)}
        client interested: {str(self._am_interested)}
        peer choking: {str(self._peer_choking)}
        peer interested: {str(self._peer_interested)})'''
        return stateLog

#Inital base state where all false
INITIAL = _PeerState(
    am_choking=False,
    am_interested=False,
    peer_choking=False,
    peer_interested=False
)

#Initalizing download states

#Base state where self not interested and peer not choking
D0 = _PeerState(
    am_choking=True,
    am_interested=False,
    peer_choking=True,
    peer_interested=False
)

#self interested but peer choking
D1 = _PeerState(
    am_choking=True,
    am_interested=True,
    peer_choking=True,
    peer_interested=False
)

#self interested and peer not choking
D2 = _PeerState(
    am_choking=True,
    am_interested=True,
    peer_choking=False,
    peer_interested=False
)

#state all none
DNONE = _PeerState(
    am_choking=False,
    am_interested=False,
    peer_choking=False,
    peer_interested=False
)
DNONE.set_none()

#initalizing upload states

#Base state where self not interested and peer not choking
U0 = _PeerState(
    am_choking=True,
    am_interested=False,
    peer_choking=True,
    peer_interested=False
)

#self interested but peer choking
U1 = _PeerState(
    am_choking=True,
    am_interested=True,
    peer_choking=True,
    peer_interested=False
)

#self interested and peer not choking
U2 = _PeerState(
    am_choking=True,
    am_interested=True,
    peer_choking=False,
    peer_interested=False
)

#state all none
UNONE = _PeerState(
    am_choking=False,
    am_interested=False,
    peer_choking=False,
    peer_interested=False
)
UNONE.set_none()