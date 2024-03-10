class Torrent():
    def __init__(self):
        self.tracker_endpoints = []  # List of tuples - (ip_address, port) each taken from a tracker url (urls are extracted from announce-list in metadata - to start, support only HTTP URLs)
        self.total_length = 0   # Total file length in bytes
        self.piece_length = 0   # Piece size in bytes
        self.pieces = ''        # Concatenation of all 20-byte SHA1 hash values
        self.pieces_count = 0   # Number of required pieces: int(len(self.total_length) / self.piece_length)
    

    # Read .torrent metadata from a bencoded file
    @staticmethod
    def read_metadata(file_path: str):
        pass

