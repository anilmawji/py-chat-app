import hashlib

class Piece:
    def __init__(self, index: int, length: int, sha1_hash: bytes):
        self.index = index
        self.length = length
        self.sha1_hash = sha1_hash
        self.is_verified = False
        self.is_downloaded = False
        self.data = None

    def valid(self, data: bytes):
        return self.sha1_hash == hashlib.sha1(data)
